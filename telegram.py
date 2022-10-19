from backend.credentials import *
from backend.flightTracking import *
from backend.database import *
import telebot
import zulu
from telebot import types
from telebot.types import InlineKeyboardButton


def main():
    currentFlightUsers = {}

    loadKeys("backend/credentials.txt")
    bot = telebot.TeleBot(getKey("Telegram"))

    # Handles start and help commands
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        print('start')
        bot.send_message(message.chat.id, "*hello*", parse_mode="markdown")

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
                            emojis[flightNum], callback_data=flight['Registration'])
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
                    for flight in currentFlightUsers[call.from_user.id]['flightList']:
                        if flight['Registration'] == call.data:
                            currentFlightUsers[call.from_user.id]['pickedFlights'].append(
                                flight)

                case 'checkForMoreFlights':
                    # TODO: Save data to database
                    if call.data == 'no':
                        print(
                            currentFlightUsers[call.from_user.id]['pickedFlights'])
                        bot.edit_message_text(chat_id=call.message.chat.id,
                                              text='Flight screne here', message_id=call.message.id)
                        del currentFlightUsers[call.from_user.id]
                    else:
                        bot.edit_message_text(
                            chat_id=call.message.chat.id, text='Please send me your flight number, ex: UA123', message_id=call.message.id)
                        currentFlightUsers[call.from_user.id]['mode'] = 'trackFlight'

    print("Bot Loaded")
    bot.infinity_polling()


# def captureFlightNum():


if (__name__ == "__main__"):
    main()
