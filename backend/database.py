import sqlite3

# precondition: data is a tuple of 13 members. This matches the Flight Database
# postcondition: data successfully entered into Flight table.


def addToFlightDB(data):
    try:
        con = sqlite3.connect("flighty.db")
        cur = con.cursor()

        cur.execute(
            "INSERT INTO Flight VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
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
        con = sqlite3.connect("flighty.db")
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
        # generate schema for Session
        cur.execute("""
            CREATE TABLE `Session` (
                `UserID` INT NOT NULL,
                `MessageID` INT,
                `NumFlights` INT NOT NULL,
                PRIMARY KEY (`UserID`)
            );
        """)

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
    return
