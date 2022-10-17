from urllib import response
import discord
from discord.ext import commands
from backend.credentials import *
from backend.flightTracking import *
from backend.credentials import *
from backend.database import *
import zulu

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)
emoteList = ['🐼','🐶','🐱','🦄','🐷','🐻‍❄️','🐋','🥳','🎈','💩']

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
                flightID = str(flight["flightID"])
                flightDelay = str(flight["Delay"])
                flightDepTime = str(flight["DepTime"])
                flightArvTime = str(flight["ArvTime"])
                flightDepTerm = str(flight["DepTerm"])
                flightDepGate = str(flight["DepGate"])
                flightArvTerm = str(flight["ArvTerm"])
                flightArvGate = str(flight["ArvGate"])
                flightArvCode = str(flight["ArvCode"])
                flightDepCode = str(flight["DepCode"])
                flightRegistration = str(flight["Registration"])

                ArvTime = zulu.parse(flight['ArvTime'])
                DepTime = zulu.parse(flight['DepTime'])

                formattedArrival = ArvTime.format('%b %d %Y - %I:%M %p %Z', tz=flight['ArvTz'])
                formattedDeaprture = DepTime.format('%b %d %Y - %I:%M %p %Z', tz=flight['DepTz'])

                myEmbed = discord.Embed(title=f"Flight Tracker: {flight_code}\t{flightDepCode} ✈️ {flightArvCode}")
                myEmbed.add_field(name = "Departure & Arrival", value=f"Departing: {formattedDeaprture} Arriving: {formattedArrival}", inline=False)

                if(int(flightDelay) > 0):
                    myEmbed.add_field(name= "Delay", value=f"{flightDelay} minute(s).", inline = True)

                myEmbed.add_field(name="Departing Gate & Terminal", value=f"Terminal: {flightDepTerm} Gate: {flightDepGate}", inline=False)
                myEmbed.add_field(name="Arriving Gate & Terminal", value=f"Terminal: {flightArvTerm} Gate: {flightArvGate}", inline=False)
                await ctx.respond(embed=myEmbed)
        #if more than 1 exists in the API call, ask the user which flight time they are referring to

        #show the user their accurate flight information.

        #here we are certain the flight exists, we serve the data to the user.

        #this statement is if only one flight exists in flights{}
        elif(len(flightData) == 1):
            await ctx.respond("hello world")
            

def main():
    loadKeys("backend/credentials.txt")
    bot.run(getKey("Discord"))

if (__name__ == "__main__"):
    main()