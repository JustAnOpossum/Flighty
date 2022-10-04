import sqlite3
from os.path import exists
from flightTracking import *
from credentials import *

def main():
    #if the database does not exist, we must make it, otherwise do nothing
    if(not exists("flighty.db")):
        makeDB("flighty.db")
    else: print("The Database already exists, skipping database creation.")

    #Loads keys for different apps
    if (not exists("credentials.txt")):
        print("No credentials file found")
        return
    else:
        print("Loading keys...")
        loadKeys("credentials.txt")
    #get a flight code from user
    #flightCode = input("Please Enter a Flight which you wish to track:\n")
    #searcg flight tracker to see if flight exists
    #flightData = getFlight(flightCode)
    #if flight does not exist, print an error
        #FIXME
    #if flight does exist, print the response / json
    #print(flightData)

def makeDB(fName):
    try:    
        #connect to and initialize the database file
        con = sqlite3.connect(fName)
        cur = con.cursor()
        #generate schema for Session
        cur.execute("""
            CREATE TABLE `Session` (
                `UserID` INT NOT NULL,
                `MessageID` INT,
                `NumFlights` INT NOT NULL,
                PRIMARY KEY (`UserID`)
            );
        """)

        #Generate schema for Flight
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
                `Coords` VARCHAR NOT NULL
            );
        """)
        #close the connection
        con.close()
    #exception error handling    
    except sqlite3.Error as er:
        print(er + " in MakeDB()")

if(__name__ == "__main__"):
    main()