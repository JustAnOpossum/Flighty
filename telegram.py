from backend.credentials import *
from backend.flightTracking import *
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def main():
    currentFlightUsers = {}

    loadKeys("backend/credentials.txt")
    bot = telebot.TeleBot(getKey("Telegram"))

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        print('start')
        bot.reply_to(message, "Welcome to the bot")

    @bot.message_handler(commands=['trackFlight'])
    def trackFlight(message):
        print('track flight')
        bot.send_message(
            message.chat.id, "Please send me your flight number, ex: UA123")
        currentFlightUsers[message.from_user.id] = {
            'mode': 'trackFlight'}

    @bot.message_handler(func=lambda message: True)
    def handleCallback(message):
        if message.from_user.id in currentFlightUsers:
            match currentFlightUsers[message.from_user.id]['mode']:
                case 'trackFlight':
                    # Gets flight information from the API
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    flights = getFlight(message.text)
                    chatMsg = "Choose a flight:"
                    flightNum = 1
                    for flight in flights:
                        flightBtn = InlineKeyboardButton(
                            flightNum, callback_data=flight['Registration'])
                        markup.add(flightBtn)
                        chatMsg += "\n" + str(flightNum) + "\n**Flight Number: " + \
                            flight['flightID'] + "(" + flight['DepCode'] + "->" + flight['ArvCode'] + ") \n**Departure Time:** " + \
                            flight['DepTime'] + \
                            "\n**Arival Time:** " + flight['ArvTime'] + "\n"
                        flightNum += 1
                    bot.send_message(message.chat.id, chatMsg,
                                     reply_markup=markup, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "Please use a command")

    @bot.callback_query_handler(func=lambda call: True)
    def test_callback(call):
        print('called')

    print("Bot Loaded")
    bot.infinity_polling()


# def captureFlightNum():


if (__name__ == "__main__"):
    main()
