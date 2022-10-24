import sqlite3

# precondition: data is a tuple of 13 members. This matches the Flight Database
# postcondition: data successfully entered into Flight table.


def addToFlightDB(data):
    try:
        con = sqlite3.connect("backend/flighty.db")
        cur = con.cursor()

        cur.execute(
            "INSERT INTO Flights VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
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
                `DepartTerminal` VARCHAR NOT NULL,
                `DepartGate` VARCHAR NOT NULL,
                `ArriveTerminal` VARCHAR NOT NULL,
                `ArriveGate` VARCHAR NOT NULL,
                `ArriveAPC` VARCHAR NOT NULL,
                `DepartAPC` VARCHAR NOT NULL,
                `ArvTz` VARCHAR NOT NULL,
                `DepTz` VARCHAR NOT NULL,
                `Registration` VARCHAR NOT NULL
            );
        """)
        # close the connection
        con.close()
    # exception error handling
    except sqlite3.Error as er:
        print(str(er) + "Test")
    return


def main():
    makeDB("flighty.db")


if (__name__ == "__main__"):
    main()
