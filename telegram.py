from backend.credentials import *
from backend.flightTracking import *
import telebot
import zulu
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


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
            'mode': 'trackFlight'}

    # Handles any message
    @bot.message_handler(func=lambda message: True)
    def handleCallback(message):
        # Makes sure user has issued a command to the bot
        if message.from_user.id in currentFlightUsers:
            match currentFlightUsers[message.from_user.id]['mode']:
                case 'trackFlight':
                    # Gets flight information from the API
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    flights = getFlight(message.text)
                    flights.reverse()
                    chatMsg = "Choose a flight:"
                    flightNum = 0
                    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
                    # Formats each flight and makes sure it has a button
                    for flight in flights:
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
                    bot.send_message(message.chat.id, chatMsg,
                                     reply_markup=markup, parse_mode="markdown")
        # Case when no command is used
        else:
            bot.send_message(message.chat.id, "Please use a command")

    # Handler for callback buttons
    @bot.callback_query_handler(func=lambda call: True)
    def test_callback(call):
        print('called')

    print("Bot Loaded")
    bot.infinity_polling()


# def captureFlightNum():


if (__name__ == "__main__"):
    main()
