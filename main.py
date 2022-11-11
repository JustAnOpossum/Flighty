import sqlite3
from os.path import exists
from typing import List
from backend.flightTracking import *
from backend.credentials import *
from backend.database import *
import zulu
from datetime import *
import pytz
import threading
import atexit
import subprocess


def main():
    # if the database does not exist, we must make it, otherwise do nothing
    if (not exists("backend/flighty.db")):
        makeDB("backend/flighty.db")

    # Loads keys for different apps
    if (not exists("backend/credentials.txt")):
        print("No credentials file found")
        return
    loadKeys("backend/credentials.txt")

    # Starts timer for updating current flight information
    timer = threading.Timer(180.0, updateFlightStatus)
    timer.start()

    # Timer to cleanup the database
    timer = threading.Timer(86400.0, deleteOldFlights)
    timer.start()

    # Starts telegram as a subprocess
    telegram = subprocess.Popen(['python', 'telegram.py'])
    # Starts discord as a subprocess
    discord = subprocess.Popen(['python', 'flightyDiscord.py'])

    # Kills telegram and discord when the main function exists
    def cleanup():
        telegram.kill()
        discord.kill()

    # Registers a function to call when the program exists
    atexit.register(cleanup)

    return  # end main

# Called every couple minutes to update the departure and arrival status of the flights


def updateFlightStatus():
    loadKeys("backend/credentials.txt")
    allFlights = getAllFlights()
    utc = pytz.UTC
    if allFlights == None:
        return
    for flight in allFlights:
        # Case for if the flight hasn't left yet
        if flight[18] == 'No':
            flightLeavesTime = (zulu.parse(flight[7]) - utc.localize(
                datetime.now())).total_seconds()
            hoursLeft = divmod(flightLeavesTime, 3600)
            # Checks to make sure the flight is close to departing, so we don't get the wrong information
            if int(hoursLeft[0]) == 0:
                flightLoc = getFlightLocation(flight[16])
                if len(flightLoc) != 0:
                    updateDeparture(
                        "Yes", "No", flight[3], flight[2], flight[0])
        # Case for if the flight is in the air
        else:
            flightLoc = getFlightLocation(flight[16])
            # Updates if the flight is no longer trackable, meaning it landed
            if len(flightLoc) == 0:
                updateDeparture("Yes", "Yes", flight[3], flight[2], flight[0])
            # Case if the flight is reporting it is on the ground
            else:
                if flightLoc['alt'] == 'ground':
                    updateDeparture(
                        "Yes", "Yes", flight[3], flight[2], flight[0])
    # Keeps the method running in the background
    timer = threading.Timer(180.0, updateFlightStatus)
    timer.start()

# Method that runs every day that looks thought the database and deletes the flights older than 5 days


def deleteFlightsTimer():
    deleteOldFlights()
    timer = threading.Timer(86400.0, deleteOldFlights)
    timer.start()


if (__name__ == "__main__"):
    main()
