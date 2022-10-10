from credentials import *
import telebot


def main():
    loadKeys("credentials.txt")
    bot = telebot.TeleBot(getKey("Telegram"))

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "Welcome to the bot")

    @bot.message_handler(commands=['trackFlight'])
    def trackFlight(message):
        bot.reply_to(message, "Testing123")

    print("Bot Loaded")
    bot.infinity_polling()


if (__name__ == "__main__"):
    main()
