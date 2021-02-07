import os
from typing import List
import re
from datetime import timedelta, datetime

import discord
from pyowm import OWM

import dateparser

# TODO: Add modifier for day/night
weather_icons = {
    "clear sky": "☀️",
    "few clouds": "🌤️",
    "scattered clouds": "☁️",
    "shower rain": "🌧️",
    "rain": "🌧️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
}

burnaby_lat_long = (49.2488, 122.9805)
burnaby_at = 'Burnaby, BC, CA'
re_activity = re.compile(r'^((?:run)|(?:walk))\?')
re_activity_at = re.compile(r'((?:run)|(?:walk)) at (.*)\?')

help_message = '''
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
    dt: datetime = dateparser.parse(time_string)
    ask = dt - timedelta(days=1)
    w = mgr.forecast_at_place(burnaby_at, '3h').get_weather_at(ask)
    return format_weather_message(w, time_string)

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
        msg += f"\n{get_weather_forecast_message(purposed_time)}"
        await message.channel.send(msg)

    groups = re_activity.findall(msg_body)
    if len(groups) > 0:
        msg = f"**{clean_discord_name(message.author.name)}** wants to **{groups[0]}**. Who's in? @here"
        msg += f"\n{get_weather_message()}"
        await message.channel.send(msg)

    elif "weather?" in msg_body:
        msg = get_weather_message()
        await message.channel.send(msg)

token = os.getenv('BOT_TOKEN')
client.run(token)