# -*- coding: utf-8 -*-

# Copyright (C) 2016 Osmo Salomaa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Public transport stops and departures from ASEAG, Aachen Germany.
API not seperately documented but uses URA interface like TfL.
See: http://content.tfl.gov.uk/tfl-live-bus-river-bus-arrivals-api-documentation.pdf
"""

import pan
import re
import urllib.parse
import json

from operator import itemgetter

RETURN_LIST = [
    "StopPointName",
    "StopID",
    "StopPointState",
    "StopPointIndicator",
    "Latitude",
    "Longitude",
    "VisitNumber",
    "TripID",
    "VehicleID",
    "LineID",
    "LineName",
    "DirectionID",
    "DestinationName",
    "DestinationText",
    "EstimatedTime",
    "BaseVersion",
]

def find_departures(stops):
    params = {
        "ReturnList": ",".join(RETURN_LIST),
        "StopID": ",".join(map(str, stops)),
    }
    url = format_url("/instant_V2", **params)
    request = pan.http.get(url, encoding="utf_8")
    data = parsejson_find_departures(request)
    return sorted(data, key=itemgetter("time"))

def parsejson_find_departures(data):
    output = []
    for line in data.splitlines():
        linelist = json.loads(line)
        if linelist[0] == 1:
            output.append({
                "destination": linelist[11],
                "line": linelist[9],
                "realtime": True,
                "scheduled_time": linelist[15]/1000,
                "stop": linelist[2],
                "time": linelist[15]/1000,
                "x": linelist[6],
                "y": linelist[5],
            })
    return output

def find_lines(stops):
    params = {
        "ReturnList": ",".join(RETURN_LIST),
        "StopID": ",".join(map(str, stops)),
    }
    url = format_url("/instant_V2", **params)
    request = pan.http.get(url, encoding="utf_8")
    data = parsejson_find_lines(request)
    return sorted(data, key=itemgetter("name"))

def parsejson_find_lines(data):
    output = []
    for line in data.splitlines():
        linelist = json.loads(line)
        if linelist[0] == 1:
            newdict = {
                "destination": linelist[11],
                "id": linelist[9],
                "name": linelist[9],
            }
            if newdict not in output:
                output.append(newdict)
    return output

def find_nearby_stops(x, y):
    radius = 500
    params = {
        "Circle": str(y)+","+str(x)+","+str(radius),
        "ReturnList": ",".join(RETURN_LIST),
    }
    url = format_url("/instant_V2", **params)
    request = pan.http.get(url, encoding="utf_8")
    return parsejson_find_nearby_stops(request)

def parsejson_find_nearby_stops(data):
    output = []
    init = True
    oldStop = ""
    line_summary = ""
    for line in data.splitlines():
        linelist = json.loads(line)
        if linelist[0] == 1:
            line_summary_substring = linelist[9] + " -> " + linelist[11]
            if oldStop != linelist[2]:
                if init == False:
                    newdict = {
                        "color": "#bb0032",
                        "description": linelist[1],
                        "id": linelist[2],
                        "name": linelist[1],
                        "line_summary": line_summary,
                        "x": linelist[6],
                        "y": linelist[5],
                    }
                    output.append(newdict)
                line_summary = line_summary_substring
            else:
                if not line_summary_substring in line_summary:
                    line_summary = line_summary + ", " + line_summary_substring
            oldStop = linelist[2]
            init = False
    return output

def find_stops(query, x, y):
    params = {
        "maxResults": "10",
        "searchString": query,
        "searchTypes": "STOPPOINT",
    }
    url = format_url("/location", **params)
    request = pan.http.get_json(url, encoding="utf_8")
    return parsejson_find_stops(request)

def parsejson_find_stops(data):
    output = []
    data = data["resultList"]
    for line in data:
        output.append({
            "color": "#bb0032",
            "description": line["stopPointName"],
            "id": line["stopPointId"],
            "line_summary": "",
            "name": line["stopPointName"],
            "x": line["longitude"],
            "y": line["latitude"],
        })
    return output

def format_url(path, **params):
    """Return API URL for `path` with `params`."""
    url = "http://ivu.aseag.de/interfaces/ura{}".format(path)
    params = "&".join("=".join(x) for x in params.items())
    return "?".join((url, params))
