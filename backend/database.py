import sqlite3

# precondition: data is a tuple of 13 members. This matches the Flight Database
# postcondition: data successfully entered into Flight table.


def addToFlightDB(data):
    try:
        con = sqlite3.connect("backend/flighty.db")
        cur = con.cursor()

        cur.execute(
            "INSERT INTO Flights VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
        con.commit()
        con.close()
    except sqlite3.Error as er:
        print(er)
    return

# precondition: the flighty.db file exists.
# postcondition: returned list of tuples containing the data from the Flight db


def queryDB(query):
    try:
        # initialize our db connection
        con = sqlite3.connect("backend/flighty.db")
        cur = con.cursor()
        # execute the query
        result = cur.execute(query)
        result = result.fetchall()  # result now holds our list
        return result
    except sqlite3.Error as er:  # error handling
        print(er)
        return None


# precondition: the flighty.db file does not exist
# postcondition: flighty.db database has properly been created
#   with tables that contain tuples of the information we need in
#   order to serve users a proper experience
def makeDB(fName):
    try:
        # connect to and initialize the database file
        con = sqlite3.connect(fName)
        cur = con.cursor()
        # Generate schema for Flight
        cur.execute("""
            CREATE TABLE `Flights` (
                `UserID` VARCHAR NOT NULL,
                `ChannelID` VARCHAR NOT NULL,
                `MessageID` VARCHAR NOT NULL,
                `FlightCode` VARCHAR NOT NULL,
                `LastMessageUpdate` DATETIME NOT NULL,
                `Delay` VARCHAR NOT NULL,
                `DepartureTime` DATETIME NOT NULL,
                `SchedArrivalTime` DATETIME NOT NULL,
                `DepartTerminal` VARCHAR,
                `DepartGate` VARCHAR,
                `ArriveTerminal` VARCHAR,
                `ArriveGate` VARCHAR,
                `ArriveAPC` VARCHAR NOT NULL,
                `DepartAPC` VARCHAR NOT NULL,
                `ArvTz` VARCHAR NOT NULL,
                `DepTz` VARCHAR NOT NULL,
                `Registration` VARCHAR NOT NULL,
                `Platform` VARCHAR NOT NULL,
                `Departed` VARCHAR NOT NULL,
                `Landed` VARCHAR NOT NULL,
                `Route` VARCHAR
            );
        """)
        # close the connection
        con.close()
    # exception error handling
    except sqlite3.Error as er:
        print(str(er) + "Test")
    return

# postcondition: Returns flight messages sorted by flight departure time
# Only gets messages for telegram


def getFlightMessage(msgID):
    try:
        # initialize our db connection
        con = sqlite3.connect("backend/flighty.db")
        cur = con.cursor()
        # execute the query
        result = cur.execute(
            'SELECT * FROM Flights WHERE MessageID = ? ORDER BY DepartureTime', (msgID,))
        result = result.fetchall()  # result now holds our list
        return result
    except sqlite3.Error as er:  # error handling
        print(er)
        return None

# returns the messageID


def getFlightMessageViaMID(messageID):
    try:
        # initialize our db connection
        con = sqlite3.connect("backend/flighty.db")
        cur = con.cursor()
        # execute the query
        result = cur.execute(
            'SELECT * FROM Flights WHERE MessageID = ? ORDER BY DepartureTime', (messageID,))
        result = result.fetchall()  # result now holds our list
        return result
    except sqlite3.Error as er:  # error handling
        print(er)
        return None

# postcondition: Returns flight messages sorted by flight departure time using user ID and message ID to filter the results


def getFlightMessageWithMessage(msgID, UserID):
    try:
        # initialize our db connection
        con = sqlite3.connect("backend/flighty.db")
        cur = con.cursor()
        # execute the query
        result = cur.execute(
            'SELECT * FROM Flights WHERE MessageID = ? AND UserID = ? ORDER BY DepartureTime', (msgID, UserID))
        result = result.fetchall()  # result now holds our list
        return result
    except sqlite3.Error as er:  # error handling
        print(er)
        return None

# postcondition: Deletes a flight from the database, called when the user wants to stop tracking a flight and delete it


def deleteFlight(flightID, msgID, userID):
    # initialize our db connection
    con = sqlite3.connect("backend/flighty.db")
    cur = con.cursor()
    cur.execute(
        'DELETE FROM Flights WHERE MessageID = ? AND UserID = ? AND FlightCode = ?', (msgID, userID, flightID))
    con.commit()

# postcondition: Returns all active user IDs


def getMsgs():
    try:
        # initialize our db connection
        con = sqlite3.connect("backend/flighty.db")
        cur = con.cursor()
        # execute the query
        result = cur.execute(
            'SELECT DISTINCT MessageID FROM Flights')
        result = result.fetchall()  # result now holds our list
        return result
    except sqlite3.Error as er:  # error handling
        print(er)
        return None

#precondition, there exist some flights that have not landed and were added using the discord platform
def getDiscordFlights():
    try:
        con = sqlite3.connect("backend/flighty.db")
        cur = con.cursor()
        #execute the query
        result = cur.execute('SELECT * FROM Flights WHERE Landed = "No" AND Platform = "Discord"')
        result = result.fetchall()
        return result
    except sqlite3.Error as er:
        print(er)
        return None
#postcondition, a list of flights on the discord platform, or None if an error was thrown

# postcondition: Returns all flights
def getAllFlights():
    try:
        # initialize our db connection
        con = sqlite3.connect("backend/flighty.db")
        cur = con.cursor()
        # execute the query
        result = cur.execute(
            'SELECT * FROM Flights WHERE Landed="No"')
        result = result.fetchall()  # result now holds our list
        return result
    except sqlite3.Error as er:  # error handling
        print(er)
        return None


# postcondition: Updates if a flight has departed in the database
def updateDeparture(departedStr, landedStr, flightID, msgID, userID):
    # initialize our db connection
    con = sqlite3.connect("backend/flighty.db")
    cur = con.cursor()
    cur.execute(
        'UPDATE Flights SET Departed = ?, Landed = ? WHERE MessageID = ? AND UserID = ? AND FlightCode = ?', (departedStr, landedStr, msgID, userID, flightID))
    con.commit()

# postcondition: Deletes all flights with arrival times older than 5 days
def deleteOldFlights():
    # initialize our db connection
    con = sqlite3.connect("backend/flighty.db")
    cur = con.cursor()
    cur.execute(
        'DELETE FROM Flights WHERE DepartureTime <= date("now", "-5 day")')
    con.commit()


def main():
    makeDB("backend/flighty.db")


if (__name__ == "__main__"):
    main()
