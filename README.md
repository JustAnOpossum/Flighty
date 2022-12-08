# Flighty - A Flight Tracking Bot

<img src="https://i.ibb.co/pvT43Fb/Publication1.png" alt="drawing" width="200"/>

# What is Flighty?

### Flighty is a bot for Telegram and Discord that lets you track your flights live.

* Live Flight Tracking
* Map of plane location
* Airport information
* Helpful for frequent fliers

# How to Get Flighty?

### Flghty is currently only on Discord and Telegram

[Add On Telegram](https://t.me/flighty_bot)

[Add On Discord](https://forceofwill.dev/flighty)

# How to Run Flighty
Requirements:
* Python >= 3.10

Credentials:

```sh
cp backend/credentials.txt.example credentials.txt
```
Edit the credentials files to save the keys that you want to use with the bot

```sh
python3 -m venv flightyVenv
source flightyVenv/bin/activate
pip install -r requirements.txt
python main.py
```