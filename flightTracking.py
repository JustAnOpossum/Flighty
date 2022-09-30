#https://flightaware.com/aeroapi/portal/documentation#get-/alerts

import requests
import json

#Tracks a single flight and returns important information
def getFlight(flightID):
    # apiKey = "UtAeSw40Z24kerztlv9fuBX4OI24Ey7A"
    # apiUrl = "https://aeroapi.flightaware.com/aeroapi/"
    # auth_header = {'x-apikey':apiKey}
    
    # response = requests.get(apiUrl + f"flights/{flightID}", headers=auth_header)
    flights = []
        
    # if response.status_code == 200:

    # else:
    #     return []
    f = open('flights.json')
    flightJSON = json.load(f)
    for flight in flightJSON['flights']:
        #Checks to make sure the flight isn't in the past
        if flight['actual_in'] == "None":
            flights.append({
                'flightID':flight['ident'],
                'Delay':flight['departure_delay'],
                'DepTime':flight['estimated_out'],
                'ArvTime':flight['estimated_in'],
                'DepTerm':flight['terminal_origin'],
                'DepGate':flight['gate_origin'],
                'ArvTerm':flight['terminal_destination'],
                'ArvGate':flight['gate_destination'],
                'ArvCode':flight['destination']['code_iata'],
                'DepCode':flight['origin']['code_iata']
                })
    f.close()
    return flights


#Tracks more than one flight and returns information
#Input is an array of many flights
def getManyFlights(flightIDs):
    allFlights = []
    for flight in flightIDs:
        allFlights.append(getFlight(flight))
    return allFlights

#Gets the current location for a flight, returning its corrdiantes
def getFlightLocation(flightID):
    return

getFlight('1')