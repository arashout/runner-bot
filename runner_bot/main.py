import discord
import os

from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps

from typing import List

help_message = '''
**Available Commands:**
type **run?** to @ everyone in the chat and get the weather
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

def get_weather_message() -> str:
    observation = mgr.weather_at_place('Burnaby, BC, CA')
    w = observation.weather
    return f"**Weather**\t{w.detailed_status}\t{w.temperature('celsius')['temp']}°C\train?: {w.rain}"

# TODO: Add code to handle time based requests... e.g. run at 4? 
# TODO: Use emojis or symbols for weather
@client.event
async def on_message(message :discord.Message):
    if message.author == client.user:
        return
    
    if mentions_user_id(message.mentions, client.user.id):
        await message.channel.send(help_message)
        return

    msg_body: str = message.content.lower()
    if "run?" in msg_body:
        msg = f"**{clean_discord_name(message.author.name)}** wants to **run**. Who's in? @here"
        msg += f"\n{get_weather_message()}"
        await message.channel.send(msg)
    if "weather?" in msg_body:
        msg = get_weather_message()
        await message.channel.send(msg)

token = os.getenv('BOT_TOKEN')
client.run(token)