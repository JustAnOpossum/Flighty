from datetime import datetime
from backend.credentials import *
from backend.flightTracking import *
from backend.database import *
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
    def test_callback(call):
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
                        for flight in currentFlightUsers[call.from_user.id]['pickedFlights']:
                            dateTime = strftime(
                                "%Y-%m-%d %H:%M:%S", localtime())
                            dateTimeArv = zulu.parse(flight['ArvTime']).format(
                                '%Y-%m-%d %H:%M:%S')
                            dateTimeDep = zulu.parse(flight['ArvTime']).format(
                                '%Y-%m-%d %H:%M:%S')
                            addToFlightDB(
                                (call.from_user.id,
                                 call.message.chat.id,
                                 call.message.id,
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
                                 flight['Registration']))
                        updateMsg(False)
                        del currentFlightUsers[call.from_user.id]
                    else:
                        bot.edit_message_text(
                            chat_id=call.message.chat.id, text='Please send me your flight number, ex: UA123', message_id=call.message.id)
                        currentFlightUsers[call.from_user.id]['mode'] = 'trackFlight'

    print("Bot Loaded")

    # Starts timer for so that the bot can edit messages with new information
    timer = threading.Timer(5.0, updateMsg, args=(True,))
    timer.start()

    bot.infinity_polling()

# Method to update bot messages with new flight information


def updateMsg(firstMsg):
    loadKeys("backend/credentials.txt")
    bot = telebot.TeleBot(getKey("Telegram"))
    for user in getUsers():
        utc = pytz.UTC
        flightMsg = getFlightMessage(user[0])
        # Makes sure time zone is UTC for later use
        depTime = utc.localize(parser.parse(flightMsg[6]))
        timeNow = utc.localize(datetime.now())
        # Case for if flight has taken off
        if timeNow > depTime:
            aircraftLocation = getFlightLocation(flightMsg[16])
            if len(aircraftLocation) == 0:
                continue
            # Gets the coords of the airports
            arvAirportCoords = airports[flightMsg[12]]['location']
            depAirportCoords = airports[flightMsg[13]]['location']
            planeCoords = (aircraftLocation['lat'], aircraftLocation['lon'])
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
            msgTxt = "*Flight:* %s (%s->%s)\n\n*Flight Progress:* %s (%d%)\n*Miles Left:* %d\n\n*Departure:* %s\n*Arrival:* %s\n\n*Departure Info:* Terminal *%s* Gate *%s*\n*Arrival Info:* Terminal *%s* Gate *%s*\n" % (
                flightMsg[3], flightMsg[13], flightMsg[12], percentStr, int(
                    percentFinished*100), int(milesLeft), depString, arvString, flightMsg[8], flightMsg[9], flightMsg[10], flightMsg[11]
            )
            bot.edit_message_text(
                chat_id=flightMsg[1], message_id=flightMsg[2], text=msgTxt, parse_mode="markdown")
        # Case if flight is waiting to take off
        else:
            depString = zulu.parse(flightMsg[6]).format(
                '%b %d %Y - %I:%M %p %Z', tz=flightMsg[15])
            arvString = zulu.parse(flightMsg[7]).format(
                '%b %d %Y - %I:%M %p %Z', tz=flightMsg[14])
            flightLeavesTime = (utc.localize(
                datetime.now()) - zulu.parse(flightMsg[7])).total_seconds()
            flightLeavesStr = "*%d* Hours *%d* Minutes" % (
                int(divmod(flightLeavesTime, 3600)[0]), int(divmod(flightLeavesTime, 60)[0]))
            msgTxt = "*Flight:* %s (%s->%s)\n\n*Time until Departure:* %s\n\n*Departure:* %s\n*Arrival:* %s\n\n*Departure Info:* Terminal *%s* Gate *%s*\n*Arrival Info:* Terminal *%s* Gate *%s*\n" % (
                flightMsg[3], flightMsg[13], flightMsg[12], flightLeavesStr, depString, arvString, flightMsg[8], flightMsg[9], flightMsg[10], flightMsg[11])
            bot.edit_message_text(
                chat_id=flightMsg[1], message_id=flightMsg[2], text=msgTxt, parse_mode="markdown")
    # Restarts the timer so method can be called again
    if firstMsg:
        timer = threading.Timer(5.0, updateMsg, args=(True,))
        timer.start()


if (__name__ == "__main__"):
    # updateMsg(False)
    main()
