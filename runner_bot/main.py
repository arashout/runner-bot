import os
from typing import List
import re
from datetime import timedelta, datetime

import discord
from pyowm import OWM

import dateparser
import pyowm

# TODO: Add modifier for day/night
weather_icons = {
    "clear sky": "☀️",
    "few clouds": "🌤️",
    "scattered clouds": "☁️",
    "broken clouds": "☁️",
    "shower rain": "🌧️",
    "rain": "🌧️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
}

burnaby_lat_long = (49.267132, -122.968941)
burnaby_at = 'Burnaby, BC, CA'
re_activity = re.compile(r'^((?:run)|(?:walk))\?')
re_activity_at = re.compile(r'((?:run)|(?:walk)) at (.*)\?')

help_message = '''
RunnerBot Verson: 0.2
**Available Commands:**
type **(run|walk)?** to @ everyone and get the current weather
    e.g. **walk?**
type **(run|walk) at <time>?** to @ everyone and get the weather forecast for today
    e.g. **run at 10am?** OR **walk at 3pm?** 
type **weather?** for the current weather
**@RunnerBot** for help
'''

owm_api_key = os.getenv('OWM_KEY')
owm = OWM(owm_api_key)
mgr = owm.weather_manager()

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

def mentions_user_id(mentions: List[discord.member.Member], id: int) -> bool:
    return any([m.id == id  for m in mentions])

def clean_discord_name(name: str) -> str:
    return name.split('[')[0]

# TODO: Adjust precipation strings for forecast
def format_weather_message(w, time_string = None) -> str:
    msg = f"**Weather** at **{time_string}**\t" if time_string is not None else "**Weather**\t"
    msg += f"{weather_icons[w.detailed_status]}:{w.detailed_status}\t{w.temperature('celsius')['temp']}°C"
    if len(w.rain) > 0:
        msg += f"\t{w.rain['1h']}mm of rain in last hour"
    if len(w.snow) > 0:
        msg += f"\t{w.rain['1h']}mm of snow in last hour"
    return msg

# TODO: This logic is a bit wack probably need some fixing
def get_weather_forecast_message(time_string: str)-> str:
    # TODO: Add more options like weahter for tomorrow?
    # TODO: I don't know why but dateparser gives me 1 day ahead?
    dt: datetime = dateparser.parse(time_string, settings={'TIMEZONE': 'US/Pacific'})
    ask = dt - timedelta(days=1)
    diff = ask - datetime.now()
    hours = int(max([1, diff.total_seconds()//3600]))
    print("Trying to forecast for datetime: {}\t{}\thours ahead: {}".format(dt, ask, hours))
    try:
        oc = mgr.one_call(burnaby_lat_long[0], burnaby_lat_long[1])
        w = oc.forecast_hourly[hours]
        return format_weather_message(w, time_string)
    except pyowm.commons.exceptions.NotFoundError as e:
        print(e)
        return "Could not retrieve the **weather**"

# TODO: Fix weather formatting
def get_weather_message() -> str:
    observation = mgr.weather_at_place(burnaby_at)
    return format_weather_message(observation.weather)

# TODO: Send instructions only on DM
@client.event
async def on_message(message :discord.Message):
    if message.author == client.user:
        return
    
    if mentions_user_id(message.mentions, client.user.id):
        await message.channel.send(help_message)
        return

    msg_body: str = message.content.lower()
    # TODO: Combine regex?
    groups = re_activity_at.findall(msg_body)
    if len(groups) > 0:
        g = groups[0]
        activity = g[0]
        purposed_time = g[1]
        msg = f"**{clean_discord_name(message.author.name)}** wants to **{activity}** at **{purposed_time}**. Who's in? @here"
        try:
            msg += f"\n{get_weather_forecast_message(purposed_time)}"
        except KeyError as ke:
            print(ke)
        await message.channel.send(msg)
        return
    
    groups = re_activity.findall(msg_body)
    if len(groups) > 0:
        msg = f"**{clean_discord_name(message.author.name)}** wants to **{groups[0]}**. Who's in? @here"
        try:
            msg += f"\n{get_weather_message()}"
        except KeyError as ke:
            print(ke)
        await message.channel.send(msg)
        return
    elif "weather?" in msg_body:
        try:
            msg = get_weather_message()
            await message.channel.send(msg)
        except KeyError as ke:
            print(ke)
        
token = os.getenv('BOT_TOKEN')
client.run(token)