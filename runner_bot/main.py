#!/usr/bin/env python3

import os
from typing import List, Optional
import re
from datetime import timedelta, datetime, timezone
import json

import discord
from pyowm import OWM

import dateparser
import pyowm
import pytz

# TODO: Add modifier for day/night
weather_icons = {
    "clear sky": "☀️",
    "few clouds": "🌤️",
    "scattered clouds": "☁️",
    "broken clouds": "☁️",
    "overcast clouds":"☁️",
    "shower rain": "🌧️",
    "rain": "🌧️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
}

burnaby_lat_long = (49.267132, -122.968941)
burnaby_at = 'Burnaby, CA'

help_message = '''
Verson: 0.2
**Available Commands:**
**@RunnerBot** for help
'''

COMMAND_CHARACTOR=";"
KEYWORD_CALISTHENICS="ringz"
KEYWORD_RUN="run"
KEYWORD_WALK="walk"
KEYWORD_WEATHER="weather"

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
    icon = weather_icons.get(w.detailed_status, '?')
    msg += f"{icon}:{w.detailed_status}\t{w.temperature('celsius')['temp']}°C"
    if len(w.rain) > 0:
        msg += f"\t{w.rain['1h']}mm of rain in last hour"
    if len(w.snow) > 0:
        msg += f"\t{w.rain['1h']}mm of snow in last hour"
    return msg

# TODO: This logic is a bit wack probably need some fixing
def get_weather_forecast_message(time_string: str)-> str:
    # TODO: Add more options like weahter for tomorrow?
    # TODO: I don't know why but dateparser gives me 1 day ahead?
    dt: datetime = dateparser.parse(time_string, settings={'TIMEZONE': 'America/Los_Angeles'})
    ask = dt - timedelta(days=1)

    diff = ask - datetime.now(pytz.timezone('US/Pacific')).replace(tzinfo=None)
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

def process(message: discord.Message) -> Optional[str]:
    msg_body: str = message.content.lower()

    if COMMAND_CHARACTOR+KEYWORD_CALISTHENICS in msg_body:
        msg = f"**{clean_discord_name(message.author.name)}** wants to do **{KEYWORD_CALISTHENICS}**. Let them know you're in with a 👍 @ringers"
        return msg
    elif COMMAND_CHARACTOR+KEYWORD_RUN in msg_body:
        msg = f"**{clean_discord_name(message.author.name)}** wants to go for a **{KEYWORD_RUN}**. Let them know you're in with a 👍 @runners"
        return msg
    elif COMMAND_CHARACTOR+KEYWORD_WALK in msg_body:
        msg = f"**{clean_discord_name(message.author.name)}** wants to go for a **{KEYWORD_WALK}**. Let them know you're in with a 👍 @walkers"
        return msg
    elif COMMAND_CHARACTOR+KEYWORD_WEATHER in msg_body:
        pass

# TODO: Send instructions only on DM
@client.event
async def on_message(message :discord.Message):
    if message.author == client.user:
        return
    
    if mentions_user_id(message.mentions, client.user.id):
        await message.channel.send(help_message)
        return
    
    response = process(message)
    if response is None:
        return
    await message.channel.send(response)
 
        
token = os.getenv('BOT_TOKEN')
client.run(token)