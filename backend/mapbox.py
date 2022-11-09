import requests
from backend.credentials import *
import urllib.parse
import json


def getMap(depAirport, arvAirport, plane, path):
    #dep airpoirt (x,y)
    #arv the same
    #plane the same
    #path is the array of points
    #returns the url of the picture of the flight path.
    # Trims lat and long to be comatable with mapbox
    fdepAirport1 = float("{:.6f}".format(depAirport[0]))
    fdepAirport2 = float("{:.6f}".format(depAirport[1]))
    farvAirport1 = float("{:.6f}".format(arvAirport[0]))
    farvAirport2 = float("{:.6f}".format(arvAirport[1]))
    fplane1 = None
    fplane2 = None
    if plane != None:
        fplane1 = float("{:.6f}".format(plane[0]))
        fplane2 = float("{:.6f}".format(plane[1]))

    # Customizable params
    depAirportColor = "#4eba14"
    arvAirportColor = "#fcba03"
    pathColor = "#000000"
    width = 500
    height = 300
    geoJson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "marker-color": depAirportColor
                },
                "geometry": {
                    "coordinates": [fdepAirport2, fdepAirport1],
                    "type": "Point"
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "marker-color": arvAirportColor
                },
                "geometry": {
                    "coordinates": [farvAirport2, farvAirport1],
                    "type": "Point"
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "stroke": pathColor,
                    "stroke-width": 2
                },
                "geometry": {
                    "coordinates": [],
                    "type": "LineString"
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "marker-symbol": "airport",
                    "marker-color": depAirportColor
                },
                "geometry": {
                    "coordinates": [fplane2, fplane1],
                    "type": "Point"
                }
            }
        ],
    }

    # Case for generating map when the flight has not taken off yet
    if plane == None:
        del geoJson['features'][3]
    # Case if the route can't be loaded for any reason
    if path == None or len(path) == 0:
        del geoJson['features'][2]

    # Appends the path to the geojson
    if path != None or len(path) != 0:
        for point in path:
            geoJson['features'][2]['geometry']['coordinates'].append(point)
    requestUrl = "https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/geojson(%s)/auto/%dx%d?access_token=%s" % (urllib.parse.quote(json.dumps(geoJson, separators=(',', ':'))), width, height, getKey("mapbox")
                                                                                                                        )
    return requestUrl


if __name__ == "__main__":
    loadKeys("backend/credentials.txt")
