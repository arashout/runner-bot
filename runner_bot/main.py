import discord
import os

from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps

owm_api_key = os.getenv('OWM_KEY')
owm = OWM(owm_api_key)
mgr = owm.weather_manager()

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

# TODO: Add code for weather responses
# TODO: Add code to handle time based requests... e.g. run at 4? 
# TODO: Use emojis or symbols for weather
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if "run?" in message.content.lower():
        msg = f"{message.author} wants to run. Who's in? @here"
        observation = mgr.weather_at_place('Burnaby, BC, CA')
        w = observation.weather
        msg += f"\nWeather\t{w.detailed_status}\t{w.temperature('celsius')['temp']}°C\train?: {w.rain}"
        await message.channel.send(msg)

token = os.getenv('BOT_TOKEN')
client.run(token)