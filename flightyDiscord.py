from urllib import response
import discord
from discord.ext import commands
from backend.credentials import *
from backend.flightTracking import *
from backend.credentials import *
from backend.database import *
from time import *
import zulu

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)
emoteList = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']
emoteDict = {'1️⃣':1, '2️⃣':2, '3️⃣':3, '4️⃣':4, '5️⃣':5, '6️⃣':6, '7️⃣':7, '8️⃣':8, '9️⃣':9, '🔟':10}

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

            myEmbed = discord.Embed(title=f"Flight Tracker: {flight_code}.\t Please select which flight you are referring to:", color=0x008080)
            myRange = range(len(flightData))
            for flight in myRange:
                flightDepTime = str(flightData[flight]["DepTime"])
                flightArvTime = str(flightData[flight]["ArvTime"])
                flightArvCode = str(flightData[flight]["ArvCode"])
                flightDepCode = str(flightData[flight]["DepCode"])

                ArvTime = zulu.parse(flightArvTime)
                DepTime = zulu.parse(flightDepTime)

                formattedArrival = ArvTime.format('%b %d %Y - %I:%M %p %Z', tz=flightData[flight]['ArvTz'])
                formattedDeaprture = DepTime.format('%b %d %Y - %I:%M %p %Z', tz=flightData[flight]['DepTz'])

                myEmbed.add_field(name = f"Flight {emoteList[flight]}:", value=f"{flightDepCode} {formattedDeaprture} ✈️ {flightArvCode} {formattedArrival}", inline=False)
            
            message = await ctx.send(embed=myEmbed)

            for flight in myRange:
                await message.add_reaction(emoteList[flight])

@bot.event
async def on_raw_reaction_add(payload):
    messageSender = payload.user_id
    userID = messageSender
    #IF THE BOT REACTED, WE IGNORE IT
    if(messageSender == bot.user.id):
        return
    else:
        #THE USER RESPONDED, WE RESPOND ACCORDINGLY
        #print("someone who is not the bot reacted to the message")
        emoji = payload.emoji
        #get the channel this was in
        channel = await bot.fetch_channel(payload.channel_id)
        #get the message that was reacted to
        message = await channel.fetch_message(payload.message_id)
        #this is the emoji the user chose, just as an int.
        emoteInt = emoteDict[emoji.name]
        #yoink the flight code
        title = message.embeds[0].title
        flightCode = (title)[16:(title.index('.'))]
        flightCode = flightCode.replace(" ", "")
        #print(flightCode)
        try:
            print("Getting flight data!")
            flightData = getFlight(flightCode)
        except flightData as er:
            print(er)

        if(flightData == [] or flightData == None):
            #if the flight response is shit. this should, in theory, never be called. but i am afraid and have anxiety.
            myEmbed = discord.Embed(title="Flight Tracker", description="There was an error fetching that flight. Please try again.", color=0xFF0000)
        else:
            #here we have a array of dictionaries
            flightData = flightData[emoteInt - 1]
            print(flightData)
            #information setup
            flightID = str(flightData["flightID"])
            flightDelay = str(flightData["Delay"])
            flightDepTime = str(flightData["DepTime"])
            flightArvTime = str(flightData["ArvTime"])
            flightDepTerm = str(flightData["DepTerm"])
            flightDepGate = str(flightData["DepGate"])
            flightArvTerm = str(flightData["ArvTerm"])
            flightArvGate = str(flightData["ArvGate"])
            flightArvCode = str(flightData["ArvCode"])
            flightDepCode = str(flightData["DepCode"])
            flightRegistration = str(flightData["Registration"])
            arvTz = str(flightData["ArvTz"])
            depTz = str(flightData["DepTz"])

            ArvTime = zulu.parse(flightArvTime)
            DepTime = zulu.parse(flightDepTime)

            formattedArrival = ArvTime.format('%b %d %Y - %I:%M %p %Z', tz=flightData['ArvTz'])
            formattedDeaprture = DepTime.format('%b %d %Y - %I:%M %p %Z', tz=flightData['DepTz'])

            currentTime = strftime("%Y-%m-%d %H:%M:%S", localtime())
            
            data = (
                str(userID),
                str(channel),
                str(message),
                str(flightCode),
                str(currentTime),
                str(flightDelay),
                str(flightDepTime),
                str(flightArvTime),
                str(flightDepTerm),
                str(flightDepGate),
                str(flightArvTerm),
                str(flightArvGate),
                str(flightArvCode),
                str(flightDepCode),
                str(arvTz),
                str(depTz),
                str(flightRegistration)
            )

            #insert data into database
            try:
                addToFlightDB(data)
            except sqlite3.Error as er:
                print(str(er))

            myEmbed = discord.Embed(title=f"Flight Tracker: {flightDepCode} ✈️ {flightArvCode}", color=0x008080)
            if(int(flightDelay) > 0):
                myEmbed.add_field(name= "Delay", value=f"{flightDelay} minute(s).", inline = False)
            
            myEmbed.add_field(name="Departure & Arrival", value = f"{formattedDeaprture} -> {formattedArrival}", inline=False)

            myEmbed.add_field(name="Departing Gate & Terminal", value=f"Terminal: {flightDepTerm} Gate: {flightDepGate}", inline=False)
            myEmbed.add_field(name="Arriving Gate & Terminal", value=f"Terminal: {flightArvTerm} Gate: {flightArvGate}", inline=False)
        #print((message.embeds)[0].fields[emoteInt- 1].value)
        await message.reply(embed=myEmbed)
        return

def main():
    loadKeys("backend/credentials.txt")
    print("Starting Discord bot!")
    bot.run(getKey("Discord"))

if (__name__ == "__main__"):
    main()