# -*- coding: utf-8 -*-

# Copyright (C) 2017 Osmo Salomaa
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
Public transport stops and departures from ASEAG, Aachen, Germany.

API not seperately documented but uses URA interface like TfL.
http://content.tfl.gov.uk/tfl-live-bus-river-bus-arrivals-api-documentation.pdf
"""

import json
import pan
import urllib.parse

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
    """Return a list of departures from `stops`."""
    params = {
        "ReturnList": ",".join(RETURN_LIST),
        "StopID": ",".join(stops),
    }
    url = format_url("/instant_V2", **params)
    request = pan.http.get(url, encoding="utf_8")
    data = parsejson_find_departures(request)
    return pan.util.sorted_departures(data)

def parsejson_find_departures(data):
    output = []
    for line in data.splitlines():
        linelist = json.loads(line)
        if linelist[0] == 1:
            output.append({
                "destination": linelist[11],
                "line": linelist[9],
                "realtime": True,
                "scheduled_time": int(linelist[15]/1000),
                "stop": linelist[2],
                "time": int(linelist[15]/1000),
                "x": float(linelist[6]),
                "y": float(linelist[5]),
            })
    return output

def find_lines(stops):
    """Return a list of lines that use `stops`."""
    params = {
        "ReturnList": ",".join(RETURN_LIST),
        "StopID": ",".join(stops),
    }
    url = format_url("/instant_V2", **params)
    request = pan.http.get(url, encoding="utf_8")
    data = parsejson_find_lines(request)
    return pan.util.sorted_unique_lines(data)

def parsejson_find_lines(data):
    output = []
    for line in data.splitlines():
        linelist = json.loads(line)
        if linelist[0] == 1:
            newdict = {
                "color": "#bb0032",
                "destination": linelist[11],
                "id": linelist[9],
                "name": linelist[9],
            }
            if newdict not in output:
                output.append(newdict)
    return output

def find_nearby_stops(x, y):
    """Return a list of stops near given coordinates."""
    radius = 500
    params = {
        "Circle": "{:.6f},{:.6f},{:d}".format(y, x, radius),
        "ReturnList": ",".join(RETURN_LIST),
    }
    url = format_url("/instant_V2", **params)
    request = pan.http.get(url, encoding="utf_8")
    return parsejson_find_nearby_stops(request)

def parsejson_find_nearby_stops(data):
    output = []
    init = True
    oldStop = ""
    line_summary = []
    for line in data.splitlines():
        linelist = json.loads(line)
        if linelist[0] == 1:
            one_line_summary = "{} → {}".format(linelist[9], linelist[11])
            if oldStop != linelist[2]:
                if init == False:
                    newdict = {
                        "color": "#bb0032",
                        "description": linelist[1],
                        "id": linelist[2],
                        "line_summary": "\n".join(line_summary[:3]),
                        "name": linelist[1],
                        "x": float(linelist[6]),
                        "y": float(linelist[5]),
                    }
                    output.append(newdict)
                line_summary = [one_line_summary]
            else:
                if not one_line_summary in line_summary:
                    line_summary.append(one_line_summary)
            oldStop = linelist[2]
            init = False
    return output

def find_stops(query, x, y):
    """Return a list of stops matching `query`."""
    params = {
        "maxResults": "10",
        "searchString": urllib.parse.quote(query),
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
            "x": float(line["longitude"]),
            "y": float(line["latitude"]),
        })
    return output

def format_url(path, **params):
    """Return API URL for `path` with `params`."""
    url = "http://ivu.aseag.de/interfaces/ura{}".format(path)
    params = "&".join("=".join(x) for x in params.items())
    return "?".join((url, params))
