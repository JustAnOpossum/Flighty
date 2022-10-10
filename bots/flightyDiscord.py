#Discord.py
#Flighty Python Bot
import discord
from ... import credentials
from os import exists
'''
# Loads keys for different apps
if (not exists("../credentials.txt")):
    print("No credentials file found")
else:
    print("Loading keys...")
    loadKeys("../credentials.txt")

print(getKey("Discord"))
'''
#setting gateway intents
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

#when we try and start the bot we need to ensure a connection is made.
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

#when the bot sees a new message, we begin processing
@client.event
async def on_message(message):
    #if the message is FROM this bot
    if message.author == client.user:
        return
    #begin checking commands
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

#client.run('')