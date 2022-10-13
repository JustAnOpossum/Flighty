from urllib import response
import discord
from discord.ext import commands
from backend.credentials import *
from backend.flightTracking import *
from backend.credentials import *
from backend.database import *

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)

@bot.slash_command(name="track_flight")
async def track_flight(ctx, flight_code:discord.Option(str)):
    try:
        print("Getting flight data!")
        flightData = getFlight(flight_code)
    except flightData as er:
        print(er)
    #if the flight does not exist, return an error embed
    if(flightData == {} or flightData == None):
        myEmbed = discord.Embed(title="Flight Tracker", description="You entered a flight code that does not coorespond to an active flight. Please try again.", color=0xFF0000)
        await ctx.respond(embed=myEmbed)
    else:
        #check if multiple flights exist
        print(type(flightData))
        print(len(flightData))
        if(len(flightData) > 1):
            print("There are more than one flights with that flight code. We must ask the user which flight they are referring to.")
            for flight in flightData:
                myEmbed = discord.Embed(title=f"Flight Tracker: {flight_code}", description=str(flight))
                await ctx.respond(embed=myEmbed)
        #if more than 1 exists in the API call, ask the user which flight time they are referring to

        #show the user their accurate flight information.

        #here we are certain the flight exists, we serve the data to the user.
        #myEmbed = discord.Embed(title=f"Flight Tracker: {flight_code}", description=str(flightData))
        #await ctx.respond(embed=myEmbed)

def main():
    loadKeys("backend/credentials.txt")
    bot.run(getKey("Discord"))

if (__name__ == "__main__"):
    main()