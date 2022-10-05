# https://flightaware.com/aeroapi/portal/documentation#get-/alerts

import requests
import json
from credentials import *

loadKeys("credentials.txt")

# Tracks a single flight and returns important information


def getFlight(flightID):
    # variable setup
    apiKey = getKey('Flight_Aware')
    apiUrl = "https://aeroapi.flightaware.com/aeroapi/"
    auth_header = {'x-apikey': apiKey}
    flights = []

    # attempts to grab a response from the API
    response = requests.get(
        apiUrl + f"flights/{flightID}", headers=auth_header)

    flightJSON = response.json()

    # if the response status code returned a valid output
    if response.status_code == 200:
        for flight in flightJSON['flights']:
            # Checks to make sure the flight isn't in the past
            # FIXME if you want to show a past flight for debug / visual purposes, negate the statement below
            # if not flight['actual_in'] == "None":
            if flight['actual_in'] == None:
                flights.append({
                    'flightID': flight['ident'],
                    'Delay': flight['departure_delay'],
                    'DepTime': flight['estimated_out'],
                    'ArvTime': flight['estimated_in'],
                    'DepTerm': flight['terminal_origin'],
                    'DepGate': flight['gate_origin'],
                    'ArvTerm': flight['terminal_destination'],
                    'ArvGate': flight['gate_destination'],
                    'ArvCode': flight['destination']['code_iata'],
                    'DepCode': flight['origin']['code_iata'],
                    'Registration': flight['registration']
                })
        return flights
    # if the response is unuseable
    # else:
        print("Error retrieving flight. Check your flight code!")
        return ({})
    # print(flights[0])
    return flights


def JsonToDictEntry(jsonFilePath):
    f = open(jsonFilePath)
    # print("OPENING JSON")
    flightJSON = json.load(f)
    # print("JSON OPENED")
    f.close()
    return
# Tracks more than one flight and returns an array of flight information
# Input is an array of many flight IDs


def getManyFlights(flightIDs):
    allFlights = []
    for flight in flightIDs:
        allFlights.append(getFlight(flight))
    return allFlights

# Gets the current location for a flight, returning its corrdiantes


def getFlightLocation(registration):
    url = f"https://adsbexchange-com1.p.rapidapi.com/v2/registration/{registration}"
    headers = {
        "X-RapidAPI-Key": "2a2f553a18msh7f35c40e76dd158p12b80bjsna711362a6d9f",
        "X-RapidAPI-Host": "adsbexchange-com1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)
