from urllib import response
import discord
from discord.ext import commands, tasks
from backend.credentials import *
from backend.flightTracking import *
from backend.credentials import *
from backend.database import *
from backend.mapbox import *
from time import *
import asyncio
import zulu
import urllib.request

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)
emoteList = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']
emoteDict = {'1️⃣':1, '2️⃣':2, '3️⃣':3, '4️⃣':4, '5️⃣':5, '6️⃣':6, '7️⃣':7, '8️⃣':8, '9️⃣':9, '🔟':10}

@bot.slash_command(name="track_flight", description="Enter a flight code to begin tracking your flight. Ex. /track_flight UAL1")
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
        #print(type(flightData))
        #print(len(flightData))
    
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
            
            message = await ctx.send(embed=myEmbed, delete_after=(60*5))

            #print(type(ctx))
            
            for flight in myRange:
                await message.add_reaction(emoteList[flight])
        else:
            #one flight exists with that flight code
            print("There was one flight with this flight code.")

@bot.event
async def on_raw_reaction_add(payload):
    messageSender = payload.user_id
    userID = messageSender
    data = []
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
            didDepart = str(flightData["DidDepart"])

            ArvTime = zulu.parse(flightArvTime)
            DepTime = zulu.parse(flightDepTime)

            formattedArrival = ArvTime.format('%b %d %Y - %I:%M %p %Z', tz=flightData['ArvTz'])
            formattedDeaprture = DepTime.format('%b %d %Y - %I:%M %p %Z', tz=flightData['DepTz'])

            currentTime = strftime("%Y-%m-%d %H:%M:%S", localtime())
            #print("Current Time: " + str(currentTime))

            data = [
                str(userID),
                str(channel),
                str(message.id),
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
                str(flightRegistration),
                "Discord",
                didDepart,
                "No",
                "NULL"
            ]

            myEmbed = discord.Embed(title=f"Flight Tracker: {flightDepCode} ✈️ {flightArvCode}", color=0x008080)
            if(int(flightDelay) > 0):
                myEmbed.add_field(name= "Delay", value=f"{flightDelay} minute(s).", inline = False)
            
            myEmbed.add_field(name="Departure & Arrival", value = f"{formattedDeaprture} -> {formattedArrival}", inline=False)

            myEmbed.add_field(name="Departing Gate & Terminal", value=f"Terminal: {flightDepTerm} Gate: {flightDepGate}", inline=False)
            myEmbed.add_field(name="Arriving Gate & Terminal", value=f"Terminal: {flightArvTerm} Gate: {flightArvGate}", inline=False)
        #print((message.embeds)[0].fields[emoteInt- 1].value)
        myMessage = await message.reply(embed=myEmbed)
        FAID = flightData["FAID"]
        routes = getFlightRoute(flightData["FAID"])
        routes = json.dumps(routes)
        print("My route: " + str(routes))
        #insert data into database
        data = (
            data[0],
            data[1],
            str(myMessage.id),
            data[3],
            data[4],
            data[5],
            data[6],
            data[7],
            data[8],
            data[9],
            data[10],
            data[11],
            data[12],
            data[13],
            data[14],
            data[15],
            data[16],
            "Discord",
            didDepart,
            "No",
            routes
        )
        try:
            addToFlightDB(data)
        except sqlite3.Error as er:
            print(er)

        #start the task that updates our message
        updateTask.start(myMessage, (emoteInt - 1), FAID)
        #add the stop sign as a clickable button to signify a user would like to stop tracking a flight
        await myMessage.add_reaction('🛑')
        return

@tasks.loop(minutes=5)
async def updateTask(message, index, FAID):
    #get the flight data for this message
    myData = getFlightMessageViaMID(message.id)
    #this is a dictionary of tuples, we only need the first tuple
    myData = myData[0]

    #Begin Embed Construction
    myEmbed = discord.Embed(title=f"{myData[13]} ✈️ {myData[12]}", color=0x008080)

    #Cases:
        #Case 1: flight has landed.
        #Case 2: Flight is en route
        #Case 3: Flight is waiting to depart.
    if myData[19] == "Yes":
        #print("Flight has landed!")
        myEmbed.add_field(name="Your flight has landed! Safe travels!", value="Thank you for using Flighty!", inline=False)
        myEmbed.set_image(url="https://media.discordapp.net/attachments/322582394416791553/1042503782568837292/flightLanded.jpg?width=701&height=701")
    #if the plane is currently en route
    elif myData[18] == "Yes" and myData[19] == "No":
        #print("Flight is en route.")
        arvAirportCoords = airports[myData[12]]['location']
        depAirportCoords = airports[myData[13]]['location']
        #print("MY ORIGIN AIRPORT COoRDS IS: " + str(arvAirportCoords))
        #debug / testing
        print("MY DATA: " + str(myData))

        flightCode = myData[3]
        registration = myData[16]

        #time processing
        ArvTime = zulu.parse(myData[7])
        DepTime = zulu.parse(myData[6])

        formattedArrival = ArvTime.format('%I:%M %p %Z', tz=myData[14])
        formattedDeaprture = DepTime.format('%I:%M %p %Z', tz=myData[15])

        #if there is a reasonable (not bugged or impossible) delay, we show it to the user
        delay = int(myData[5])
        if (delay < 0 or delay > 2500):
            myEmbed.add_field(name= "Delay", value=f"{myData[5]} minute(s).", inline = False)
        
        #show departure, arrivval information
        myEmbed.add_field(name="Departure & Arrival", value = f"{formattedDeaprture} -> {formattedArrival}", inline=False)

        myEmbed.add_field(name="Departing Gate & Terminal", value=f"Terminal: {myData[8]} \nGate: {myData[9]}", inline=False)
        myEmbed.add_field(name="Arriving Gate & Terminal", value=f"Terminal: {myData[10]} \nGate: {myData[11]}", inline=False)

        currentTime = strftime("%H:%M", localtime())

        #this was a temporary debug statement to make sure the message was updating correctly
        #myEmbed.add_field(name="Last Update: ", value=f"{str(currentTime)}", inline=False)

        #get the registration code, and location data. load in the route list.
        flightRegistration = myData[16]
        locationData = getFlightLocation(flightRegistration)
        planeCoords = (locationData['lat'], locationData['lon'])
        #print("MY LOCATION DATA IS :" + str(planeCoords))
        #print("MY LOCATION DATA TYPE IS: " + str(type(planeCoords)))
        routes = myData[20]
        routes = json.loads(routes)
        #print("YOUR ROUTE IS: " + str(routes))

        #get the url that pertains to our map
        mapURL = getMap(depAirportCoords, arvAirportCoords, planeCoords, routes)
        urllib.request.urlretrieve(mapURL, "FlightMapREDACTED.jpg")
        #print("YOUR FLIGHT LOCATNON IS: " + str(locationData))
        latitude = None
        longitude = None
        if(locationData == {} or locationData == None):
            print("There was an error retrieving the flight location data.")
        else:
            latitude = locationData["lat"]
            longitude = locationData["lon"]
            #myEmbed.add_field(name="Position", value=f"Latitude: {latitude} Longitude: {longitude}", inline=False)

        myEmbed.set_image(url=mapURL)
    elif myData[19] == "No":
        #here is if the flight has not departed
        #print("Flight not departed.")
        myEmbed.add_field(name="Your flight has not departed yet! Hang tight!",value="Thank you for using Flighty!", inline=False)
        myEmbed.set_image(url="https://media.discordapp.net/attachments/322582394416791553/1042503782833061928/waitForDepart.jpg?width=701&height=701")
    #update the message
    await message.edit(embed=myEmbed)
    return

def main():
    loadKeys("backend/credentials.txt")
    print("Starting Discord bot!")
    bot.run(getKey("Discord"))

if (__name__ == "__main__"):
    main()