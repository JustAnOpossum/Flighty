from datetime import datetime
from backend.credentials import *
from backend.flightTracking import *
from backend.database import *
from backend.mapbox import *
import telebot
import zulu
import threading
from dateutil import parser
from datetime import *
import pytz
from time import *
from telebot import types
from telebot.types import InlineKeyboardButton
import geopy.distance

selectedFlight = {}


def main():
    currentFlightUsers = {}

    loadKeys("backend/credentials.txt")
    bot = telebot.TeleBot(getKey("Telegram"))

    # Handles start and help commands
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        print('start')
        bot.send_message(
            message.chat.id, "Welcome to the bot, temporary welcome message. Commands are */trackFlight*", parse_mode="markdown")

    # Handles the track flight command
    @bot.message_handler(commands=['trackFlight'])
    def trackFlight(message):
        print('track flight')
        bot.send_message(
            message.chat.id, "Please send me your flight number, ex: UA123")
        # Sets that this user is going to use this command
        currentFlightUsers[message.from_user.id] = {
            'mode': 'trackFlight', 'pickedFlights': []}

    # Handles any message
    @bot.message_handler(func=lambda message: True)
    def handleCallback(message):
        # Makes sure user has issued a command to the bot
        if message.from_user.id in currentFlightUsers:
            match currentFlightUsers[message.from_user.id]['mode']:
                case 'trackFlight':
                    currentFlightUsers[message.from_user.id]['flightList'] = []
                    # Gets flight information from the API
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    flights = getFlight(message.text)
                    flights.reverse()

                    # Makes sure a user inputs a correct flight number
                    if len(flights) == 0:
                        bot.send_message(
                            message.chat.id, "No flights found. Please try another flight number.")
                        return

                    chatMsg = "Choose a flight:"
                    flightNum = 0
                    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
                    emojiCnt = 0
                    if flights == {} or flights == None:
                        bot.send_message(message.chat.id, 'Please send me a valid flight number',
                                         reply_markup=markup, parse_mode="markdown")
                        return
                    # Formats each flight and makes sure it has a button
                    for flight in flights:
                        if emojiCnt == 5:
                            break
                        flightBtn = InlineKeyboardButton(
                            emojis[flightNum], callback_data=str(emojiCnt))
                        markup.add(flightBtn)
                        ArvTime = zulu.parse(flight['ArvTime'])
                        DepTime = zulu.parse(flight['DepTime'])
                        formattedArival = ArvTime.format(
                            '%b %d %Y - %I:%M %p %Z', tz=flight['ArvTz'])
                        formattedDeaprture = DepTime.format(
                            '%b %d %Y - %I:%M %p %Z', tz=flight['DepTz'])
                        chatMsg += "\n%s:\n*Flight Number:* %s (%s->%s)\n*Departure Time:* %s\n*Arrival Time: *%s\n" % (
                            emojis[flightNum], flight['flightID'], flight['DepCode'], flight['ArvCode'], formattedDeaprture, formattedArival)
                        flightNum += 1
                        emojiCnt += 1
                        # Saves all flight options for later use
                        currentFlightUsers[message.from_user.id]['flightList'].append(
                            flight)
                    bot.send_message(message.chat.id, chatMsg,
                                     reply_markup=markup, parse_mode="markdown")
        # Case when no command is used
        else:
            bot.send_message(message.chat.id, "Please use a command")

    # Handler for callback buttons
    @bot.callback_query_handler(func=lambda call: True)
    def btnCallback(call):
        if call.from_user.id in currentFlightUsers:
            match currentFlightUsers[call.from_user.id]['mode']:
                # Callback when a user chooses a flight from the search results
                case 'trackFlight':
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    btn1 = InlineKeyboardButton("Yes", callback_data="yes")
                    btn2 = InlineKeyboardButton("No", callback_data="no")
                    markup.add(btn1, btn2)
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          text='Do you want to track any more flights?', message_id=call.message.id, reply_markup=markup)
                    currentFlightUsers[call.from_user.id]['mode'] = 'checkForMoreFlights'
                    # Adds their current flight to picked flights for later use
                    currentFlightUsers[call.from_user.id]['pickedFlights'].append(
                        currentFlightUsers[call.from_user.id]['flightList'][int(call.data)])

                case 'checkForMoreFlights':
                    if call.data == 'no':
                        # Saves all the picked flights to the database
                        for flight in currentFlightUsers[call.from_user.id]['pickedFlights']:
                            dateTime = strftime(
                                "%Y-%m-%d %H:%M:%S", localtime())
                            dateTimeArv = zulu.parse(flight['ArvTime']).format(
                                '%Y-%m-%d %H:%M:%S')
                            dateTimeDep = zulu.parse(flight['DepTime']).format(
                                '%Y-%m-%d %H:%M:%S')

                            # Gets the route for the flight to save to the database and generates inital map
                            routes = getFlightRoute(flight['FAID'])

                            newMsg = bot.send_photo(chat_id=call.message.chat.id, caption="Loading your flight...",
                                                    photo='https://cdn.iconscout.com/icon/free/png-256/aeroplane-airplane-plane-air-transportation-vehicle-pessanger-people-emoj-symbol-30708.png')
                            addToFlightDB(
                                (call.from_user.id,
                                 call.message.chat.id,
                                 newMsg.id,
                                 flight['flightID'],
                                 dateTime, flight['Delay'],
                                 dateTimeDep,
                                 dateTimeArv,
                                 flight['DepTerm'],
                                 flight['DepGate'],
                                 flight['ArvTerm'],
                                 flight['ArvGate'],
                                 flight['ArvCode'],
                                 flight['DepCode'],
                                 flight['ArvTz'],
                                 flight['DepTz'],
                                 flight['Registration'],
                                 'Telegram',
                                 flight['DidDepart'],
                                 'No',
                                 json.dumps(routes)))
                        updateMsg(False)
                        del currentFlightUsers[call.from_user.id]
                    else:
                        bot.edit_message_text(
                            chat_id=call.message.chat.id, text='Please send me your flight number, ex: UA123', message_id=call.message.id)
                        currentFlightUsers[call.from_user.id]['mode'] = 'trackFlight'
                        # Case for user using the buttons on the flight tracking
        if ':' not in call.data:
            return
        params = call.data.split(':')
        # Checks for what each button press could be
        match params[1]:
            # Button is pressed to go to the next flight
            case 'c':
                getSelectedFlight(call.message.id, str(call.from_user.id))
                if params[0] != 'N/A':
                    selectedFlight[str(call.from_user.id)
                                   ]['selectedFlight'] = params[0]
                    updateMsg(False)
            # Button is pressed to refresh
            case 'r':
                updateMsg(False)
            # Button is pressed to stop tracking flight
            case 's':
                getSelectedFlight(call.message.id, str(call.from_user.id))
                deleteFlight(params[0], call.message.id, call.from_user.id)
                del selectedFlight[str(call.from_user.id)]
                flights = getFlightMessageWithMessage(
                    call.message.id, call.from_user.id)
                # Checks to see if there are any flights left
                if len(flights) == 0:
                    # TODO: Fix message image, (map)
                    bot.edit_message_text(
                        chat_id=call.message.chat.id, text='No Flights Left', message_id=call.message.id)
                updateMsg(False)
    print("Bot Loaded")

    # Starts timer for so that the bot can edit messages with new information
    # timer = threading.Timer(5.0, updateMsg, args=(True,))
    # timer.start()

    bot.infinity_polling()

# Method to update bot messages with new flight information


def updateMsg(firstMsg):
    loadKeys("backend/credentials.txt")
    bot = telebot.TeleBot(getKey("Telegram"))
    for user in getUsers():
        utc = pytz.UTC
        flightMsgs = getFlightMessage(user[0])
        count = 0
        # Loops though all flights for a user
        for flightMsg in flightMsgs:
            selectedFlightMsg = getSelectedFlight(
                flightMsg[2], flightMsg[0])
            # Finds the current selected message, so that it is the only one that is updated
            if selectedFlightMsg not in flightMsg[3]:
                count = count + 1
                continue

            nextFlight = ''
            prevFlight = ''
            if len(flightMsgs) != count+1 and flightMsgs[count+1][2] == flightMsg[2]:
                nextFlight = flightMsgs[count+1][3]
            else:
                nextFlight = 'N/A'
            if count-1 >= 0 and flightMsgs[count-1][2] == flightMsg[2]:
                prevFlight = flightMsgs[count-1][3]
            else:
                prevFlight = 'N/A'

            # Creates the markup buttons for the interaction with the flight tracking
            markup = types.InlineKeyboardMarkup(
                row_width=2)
            forwardBtn = InlineKeyboardButton(
                "➡️", callback_data='%s:%s' % (nextFlight, 'c'))
            backwardBtn = InlineKeyboardButton(
                "⬅️", callback_data='%s:%s' % (prevFlight, 'c'))
            stopBtn = InlineKeyboardButton(
                "🛑", callback_data='%s:%s' % (flightMsg[3], 's'))
            refreshBtn = InlineKeyboardButton(
                "🔄", callback_data='%s:%s' % (flightMsg[3], 'r'))
            markup.add(backwardBtn, forwardBtn, stopBtn, refreshBtn)
            # Case for if flight has departed
            if flightMsg[18] == "Yes":
                aircraftLocation = getFlightLocation(flightMsg[16])
                if len(aircraftLocation) == 0:
                    continue
                # Gets the coords of the airports
                arvAirportCoords = airports[flightMsg[12]]['location']
                depAirportCoords = airports[flightMsg[13]]['location']
                planeCoords = (
                    aircraftLocation['lat'], aircraftLocation['lon'])
                # Calculates how many miles left the plane has to go
                milesLeft = geopy.distance.great_circle(
                    arvAirportCoords, planeCoords).miles
                # Calculates the total distance from airport to airport
                totalDistance = geopy.distance.great_circle(
                    arvAirportCoords, depAirportCoords).miles
                # Calculates the percent finished the flight has
                percentFinished = ((totalDistance - milesLeft)/totalDistance)
                percentStr = ""
                depString = zulu.parse(flightMsg[6]).format(
                    '%b %d %Y - %I:%M %p %Z', tz=flightMsg[15])
                arvString = zulu.parse(flightMsg[7]).format(
                    '%b %d %Y - %I:%M %p %Z', tz=flightMsg[14])
                for i in range(0, 10):
                    if int(percentFinished * 10) == i:
                        percentStr = percentStr + '✈️'
                    else:
                        percentStr = percentStr + '-'
                msgTxt = "*Flight:* %s (%s🛫%s)\n\n*Flight Progress:* %s (%d Percent)\n*Miles Left:* %d\n\n*Departure:* %s\n*Arrival:* %s\n\n*Departure Info:*\nTerminal *%s*\nGate *%s*\n*Arrival Info:*\nTerminal *%s*\nGate *%s*\n" % (
                    flightMsg[3], flightMsg[13], flightMsg[12], percentStr, int(
                        percentFinished*100), int(milesLeft), depString, arvString, flightMsg[8], flightMsg[9], flightMsg[10], flightMsg[11]
                )
                routes = json.loads(flightMsg[20])
                mapUrl = getMap(airports[flightMsg[13]]['location'],
                                airports[flightMsg[12]]['location'], planeCoords, routes)
                editPhotoMessage(
                    flightMsg[2], flightMsg[1], 'https://greyopossum.net/img/full/RedPandaIcon.png', markup, bot, msgTxt)
            # Case if flight is waiting to take off
            else:
                depString = zulu.parse(flightMsg[6]).format(
                    '%b %d %Y - %I:%M %p %Z', tz=flightMsg[15])
                arvString = zulu.parse(flightMsg[7]).format(
                    '%b %d %Y - %I:%M %p %Z', tz=flightMsg[14])
                flightLeavesTime = (zulu.parse(flightMsg[7]) - utc.localize(
                    datetime.now())).total_seconds()
                hoursLeft = divmod(flightLeavesTime, 3600)
                minutesLeft = divmod(hoursLeft[1], 60)
                flightLeavesStr = "*%d* Hours *%d* Minutes" % (
                    int(hoursLeft[0]), int(minutesLeft[0]))
                msgTxt = "*Flight:* %s (%s->%s)\n\n*Time until Departure:* %s\n\n*Departure:* %s\n*Arrival:* %s\n\n*Departure Info:*\nTerminal *%s*\nGate *%s*\n*Arrival Info:*\nTerminal *%s*\nGate *%s*\n" % (
                    flightMsg[3], flightMsg[13], flightMsg[12], flightLeavesStr, depString, arvString, flightMsg[8], flightMsg[9], flightMsg[10], flightMsg[11])
                routes = json.loads(flightMsg[20])
                mapUrl = getMap(airports[flightMsg[13]]['location'],
                                airports[flightMsg[12]]['location'], None, routes)
                editPhotoMessage(
                    flightMsg[2], flightMsg[1], 'https://greyopossum.net/img/full/RedPandaIcon.png', markup, bot, msgTxt)
    # Restarts the timer so method can be called again
    if firstMsg:
        timer = threading.Timer(5.0, updateMsg, args=(True,))
        timer.start()


def getSelectedFlight(msgID, userID):
    # Create the message in the object
    if userID not in selectedFlight:
        selectedFlight[userID] = {'selectedFlight': ''}
        flight = getFlightMessageWithMessage(msgID, userID)
        if len(flight) == 0:
            return {}
        flight = flight[0]
        selectedFlight[userID] = {'selectedFlight': flight[3]}
    # Code for handaling the button presses in the flight tracking
    return selectedFlight[userID]['selectedFlight']


def editPhotoMessage(msgID, chatID, newPhotoURL, inlineKeyboard, bot, text):
    photoToSend = types.InputMediaPhoto(
        newPhotoURL)
    bot.edit_message_media(chat_id=chatID,
                           message_id=msgID, media=photoToSend)
    bot.edit_message_caption(chat_id=chatID,
                             message_id=msgID, caption=text, parse_mode="markdown", reply_markup=inlineKeyboard)


if (__name__ == "__main__"):
    # updateMsg(False)
    main()
