import requests
from credentials import *
import urllib.parse
import json


def getMap(depAirport, arvAirport, plane, path):
    # Trims lat and long to be comatable with mapbox
    fdepAirport1 = float("{:.6f}".format(depAirport[0]))
    fdepAirport2 = float("{:.6f}".format(depAirport[1]))
    farvAirport1 = float("{:.6f}".format(arvAirport[0]))
    farvAirport2 = float("{:.6f}".format(arvAirport[1]))
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
    for point in path:
        geoJson['features'][2]['geometry']['coordinates'].append(point)
    print(json.dumps(geoJson, separators=(',', ':')))
    requestUrl = "https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/geojson(%s)/auto/%dx%d?access_token=%s" % (urllib.parse.quote(json.dumps(geoJson, separators=(',', ':'))), width, height, getKey("mapbox")
                                                                                                                        )
    return requestUrl


if __name__ == "__main__":
    loadKeys("backend/credentials.txt")
    print(getMap((29.9841416, -95.3329859561449),
                 (31.8092748, -106.36664263248113),
                 (30.748848581706227, -101.64781222368353),
                 [(-95.3329859561449, 29.9841416), (-106.36664263248113, 31.8092748)]))
