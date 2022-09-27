import sqlite3
from os.path import exists

credentials = open("credentials.txt", "r")
#TODO process keys and tokens
credentials.close()

def main():
    #if the database does not exist, we must make it, otherwise do nothing
    if(not exists("flights.db")):
        makeDB("flights.db")
    else: print("The Database already exists, skipping database creation.")

def makeDB(fName):
    #connect to and initialize the database file
    con = sqlite3.connect(fName)
    cur = con.cursor()
    cur.execute("CREATE TABLE `Flight` (`FlightID` INT,PRIMARY KEY (`FlightID`));")
    con.close()

if(__name__ == "__main__"):
    main()