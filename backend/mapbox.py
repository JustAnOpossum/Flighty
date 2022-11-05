import requests
import geojson

# TODO: https://stackoverflow.com/questions/68135260/mapbox-static-api-how-to-use-custom-markers-in-geojson-overlay


def getMap(depAirport, arvAirport):
    depPoint = geojson.Point(depAirport['lon'], depAirport['lat'])
    arvPoint = geojson.Point(arvAirport['lon'], arvAirport['lat'])
