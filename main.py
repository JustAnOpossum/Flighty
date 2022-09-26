import sqlite3

def main():
    makeDB()

def makeDB():
    con = sqlite3.connect("tutorial.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE `Flight` (`FlightID` INT,PRIMARY KEY (`FlightID`));");

if(__name__ == "__main__"):
    main()