from msilib.schema import Error
import sqlite3
from os.path import exists
from typing import List
from flightTracking import *
from "../credentials" import *


def main():
    # if the database does not exist, we must make it, otherwise do nothing
    if (not exists("flighty.db")):
        makeDB("flighty.db")
    else:
        print("The Database already exists, skipping database creation.")

    # Loads keys for different apps
    if (not exists("credentials.txt")):
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
        if(isinstance(flightData, List)):
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
            con = sqlite3.connect("flighty.db")
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
            cur.execute("INSERT INTO Flight VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
            #commit issues into flighty.db
            con.commit()

            con.close()
        except sqlite3.Error as er:
            print(er)
        # get new user input
        userInput = input("Enter q to quit, press enter to continue")
    return

#precondition: a query is passed into 
def queryDB(query):
    try:
        con = sqlite3.connect("flighty.db")
        cur = con.cursor()

    except sqlite3.Error as er:
        print(er)
    return

#precondition: data is a tuple of 13 members. This matches the Flight Database
#postcondition: data successfully entered into Flight table.
def addToFlightDB(data):
    try:
        con = sqlite3.connect("flighty.db")
        cur = con.cursor()

        cur.execute("INSERT INTO Flight VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
        con.commit()
        con.close()
    except sqlite3.Error as er:
        print(er)
    return

#precondition: the flighty.db file does not exist
#postcondition: flighty.db database has properly been created 
#   with tables that contain tuples of the information we need in
#   order to serve users a proper experience
def makeDB(fName):
    try:
        # connect to and initialize the database file
        con = sqlite3.connect(fName)
        cur = con.cursor()
        # generate schema for Session
        cur.execute("""
            CREATE TABLE `Session` (
                `UserID` INT NOT NULL,
                `MessageID` INT,
                `NumFlights` INT NOT NULL,
                PRIMARY KEY (`UserID`)
            );
        """)
        #FIXME REMOVE THIS AFTER DEMO 1
        cur.execute(
            """
            INSERT INTO Session VALUES (1, 1, 1), (2, 2, 2), (3, 3, 3);
            """
        )
        #FIXME REMOVE THIS ONE TOO AFTER DEMO 1
        con.commit()

        # Generate schema for Flight
        cur.execute("""
            CREATE TABLE `Flight` (
                `UserID` VARCHAR NOT NULL,
                `InternalFlightID` INT NOT NULL,
                `Delay` INT NOT NULL,
                `DepartureTime` VARCHAR NOT NULL,
                `SchedArrivalTime` VARCHAR NOT NULL,
                `DepartTerminal` VARCHAR NOT NULL,
                `DepartGate` VARCHAR NOT NULL,
                `ArriveTerminal` VARCHAR NOT NULL,
                `ArriveGate` VARCHAR NOT NULL,
                `ArriveAPC` VARCHAR NOT NULL,
                `DepartAPC` VARCHAR NOT NULL,
                `Coords` VARCHAR NOT NULL,
                `Registration` VARCHAR NOT NULL
            );
        """)
        # close the connection
        con.close()
    # exception error handling
    except sqlite3.Error as er:
        print(er)


if (__name__ == "__main__"):
    main()
