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

    terminalChar = 'q'
    userInput = input("Enter q to quit, press enter to continue")
    while (not userInput == terminalChar):
        # get a flight code from user
        flightCode = input("Please Enter a Flight which you wish to track:\n")
        # search flight tracker to see if flight exists
        flightData = getFlight(flightCode)
        # if flight does not exist, print an error
        if (flightData == None):
            print("Flight may not exist. Try again.")
            continue
        # if flight does exist, print the response / json
        if (isinstance(flightData, List)):
            flightData = flightData[0]

        print(type(flightData))
        print(flightData)

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

        print("Flight ID: " + flightID)
        print("FLight Delay: " + flightDelay)
        print("Flight Departure Time: " + flightDepTime)
        print("Flight Arrival Time: " + flightArvTime)
        print("Flight Departure Terminal: " + flightDepTerm)
        print("Flight Departure Gate: " + flightDepGate)
        print("Flight Arrival Terminal: " + flightArvTerm)
        print("Flight Arrival Gate: " + flightArvGate)
        print("Arrival Airport Code: " + flightArvCode)
        print("Departing Airport Code: " + flightDepCode)
        print("Flight Registration Code: " + flightRegistration)

        # add this data to database
        try:
            # connect to the database
            con = sqlite3.connect("backend/flighty.db")
            cur = con.cursor()
            data = (
                "1",
                1,
                int(flightDelay),
                flightDepTime,
                flightArvTime,
                flightDepTerm,
                flightDepGate,
                flightArvTerm,
                flightArvGate,
                flightArvCode,
                flightDepCode,
                "Coordinates not implemented yet!",
                flightRegistration
            )
            cur.execute(
                "INSERT INTO Flight VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
            # commit issues into flighty.db
            con.commit()

            con.close()
        except sqlite3.Error as er:
            print(er)
        # get new user input
        userInput = input("Enter q to quit, press enter to continue")
    return  # end main


if (__name__ == "__main__"):
    main()