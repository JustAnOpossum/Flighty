import sqlite3
from os.path import exists
from typing import List
from backend.flightTracking import *
from backend.credentials import *
from backend.database import *


def main():
    # if the database does not exist, we must make it, otherwise do nothing
    if (not exists("backend/flighty.db")):
        makeDB("backend/flighty.db")
    else:
        print("The Database already exists, skipping database creation.")

    # Loads keys for different apps
    if (not exists("backend/credentials.txt")):
        print("No credentials file found")
        return
    else:
        print("Loading keys...")
        loadKeys("credentials.txt")
    return  # end main


# def updateFlightStatus():


if (__name__ == "__main__"):
    main()
