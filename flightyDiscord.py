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
emoteList = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']

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

            myEmbed = discord.Embed(title=f"Flight Tracker: {flight_code}.\t Please select which flight you are referring to:")
            myRange = range(len(flightData))
            for flight in myRange:
                flightID = str(flightData[flight]["flightID"])
                flightDelay = str(flightData[flight]["Delay"])
                flightDepTime = str(flightData[flight]["DepTime"])
                flightArvTime = str(flightData[flight]["ArvTime"])
                flightDepTerm = str(flightData[flight]["DepTerm"])
                flightDepGate = str(flightData[flight]["DepGate"])
                flightArvTerm = str(flightData[flight]["ArvTerm"])
                flightArvGate = str(flightData[flight]["ArvGate"])
                flightArvCode = str(flightData[flight]["ArvCode"])
                flightDepCode = str(flightData[flight]["DepCode"])
                flightRegistration = str(flightData[flight]["Registration"])

                ArvTime = zulu.parse(flightArvTime)
                DepTime = zulu.parse(flightDepTime)

                formattedArrival = ArvTime.format('%b %d %Y - %I:%M %p %Z', tz=flightData[flight]['ArvTz'])
                formattedDeaprture = DepTime.format('%b %d %Y - %I:%M %p %Z', tz=flightData[flight]['DepTz'])

                myEmbed.add_field(name = f"Flight {emoteList[flight]}:", value=f"{flightDepCode} {formattedDeaprture} ✈️ {flightArvCode} {formattedArrival}", inline=False)

                #if(int(flightDelay) > 0):
                    #myEmbed.add_field(name= "Delay", value=f"{flightDelay} minute(s).", inline = True)

                #myEmbed.add_field(name="Departing Gate & Terminal", value=f"Terminal: {flightDepTerm} Gate: {flightDepGate}", inline=False)
                #myEmbed.add_field(name="Arriving Gate & Terminal", value=f"Terminal: {flightArvTerm} Gate: {flightArvGate}", inline=False)
            message = await ctx.send(embed=myEmbed)
            messageID = message.id
            print(type(message))
            print(messageID)
            #print(message)
            for flight in myRange:
                await message.add_reaction(emoteList[flight])
        #if more than 1 exists in the API call, ask the user which flight time they are referring to

        #show the user their accurate flight information.

        #here we are certain the flight exists, we serve the data to the user.

@bot.event
async def on_raw_reaction_add(payload):
    messageSender = payload.user_id
    if(messageSender == bot.user.id):
        return
    else:
        print("someone who is not the bot reacted to the message")
        emoji = payload.emoji
        #get the channel this was in
        channel = await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.reply(f"You picked {emoji}")
        return

def main():
    loadKeys("backend/credentials.txt")
    bot.run(getKey("Discord"))

if (__name__ == "__main__"):
    main()