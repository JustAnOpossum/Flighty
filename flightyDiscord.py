import discord
from discord.ext import commands
from credentials import *

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents)

@bot.slash_command(name="track_flight")
async def track_flight(ctx):
    await ctx.respond("Tracking Flight!")

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

loadKeys("credentials.txt")
print(getKey("Discord"))
bot.run(getKey("Discord"))