# https://flightaware.com/aeroapi/portal/documentation#get-/alerts

import requests
import json
import csv
from backend.credentials import *

# loadKeys("credentials.txt")
# Global var for airport locations and time zones
airports = {}

try:
    # Loads airport CSV file for later use
    with open('backend/airports.csv', encoding="utf8") as airportsCSV:
        reader = csv.reader(airportsCSV, delimiter=',')
        for row in reader:
            # Adds time zone information and location for each IATA airport
            newLocation = row[5].replace("POINT (", "")
            newLocation = newLocation.replace(")", "")
            split = newLocation.split(" ")
            newLocation = (float(split[1]), float(split[0]))
            airports[row[0]] = {'tz': row[1], 'location': newLocation}
except:
    print('Error opening CSV file.')

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
            # THIS IS AN ARRAY OF DICTIONARIES
            if flight['actual_in'] == None:
                didDepart = 'No'
                if flight['actual_out'] != None:
                    didDepart = 'Yes'
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
                    'Registration': flight['registration'],
                    'ArvLocation': airports[flight['destination']['code_iata']]['location'],
                    'DepLocation': airports[flight['origin']['code_iata']]['location'],
                    'ArvTz': airports[flight['destination']['code_iata']]['tz'],
                    'DepTz': airports[flight['origin']['code_iata']]['tz'],
                    'FAID': flight['fa_flight_id'],
                    'DidDepart': didDepart
                })
        return flights
    # if the response is unuseable
    else:
        print("Error retrieving flight. Check your flight code!")
        return ({})


def getFlightRoute(FAID):
    # variable setup
    apiKey = getKey('Flight_Aware')
    apiUrl = "https://aeroapi.flightaware.com/aeroapi/"
    auth_header = {'x-apikey': apiKey}
    finalRoutes = []

    response = requests.get(
        apiUrl + f"flights/{FAID}/route", headers=auth_header)
    if response.status_code == 200:
        routeJSON = response.json()
        for route in routeJSON['fixes']:
            # Only pulls field where there are coords
            if route['latitude'] != None and route['longitude'] != None:
                lat = float("{:.6f}".format(route['latitude']))
                lon = float("{:.6f}".format(route['longitude']))
                finalRoutes.append((lon, lat))
        return finalRoutes
    else:
        print(
            "Error retrieving Route, please try again later or with a different flight code")
        return []

# Gets the current location for a flight, returning its corrdiantes


def getFlightLocation(registration):
    url = f"https://adsbexchange-com1.p.rapidapi.com/v2/registration/{registration}/"
    headers = {
        "X-RapidAPI-Key": getKey('Ads_B_Exchange'),
        "X-RapidAPI-Host": "adsbexchange-com1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)
    resposeJSON = response.json()

    if response.status_code == 200:
        if len(resposeJSON['ac']) != 0:
            # this is a dictioary
            return {
                'lat': resposeJSON['ac'][0]['lat'],
                'lon': resposeJSON['ac'][0]['lon'],
            }
        else:
            return {}
    else:
        print("Error getting flight location")
        return {}
