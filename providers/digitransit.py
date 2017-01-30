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
Public transport stops and departures in Finland from Digitransit.

http://digitransit.fi/en/developers/services-and-apis/1-routing-api/
http://dev.hsl.fi/graphql/console/
"""

import functools
import os
import pan
import re

COLORS = {
 "AIRPLANE": "#ed145d",
      "BUS": "#007ac9",
    "FERRY": "#00b9e4",
     "RAIL": "#8c4799",
   "SUBWAY": "#ff6319",
     "TRAM": "#00985f",
     "WALK": "#888888",
}

CONF_DEFAULTS = {
    # "hsl", "waltti" or "finland"
    "region": "hsl",
}

HEADERS = {"Content-Type": "application/graphql"}
URL = "http://api.digitransit.fi/routing/v1/routers/{region}/index/graphql"

def find_departures(stops):
    """Return a list of departures from `stops`."""
    stops = ", ".join('"{}"'.format(x) for x in stops)
    body = format_graphql("find_departures", ids=stops)
    url = URL.format(region=pan.conf.providers.digitransit.region)
    result = pan.http.post_json(url, body, headers=HEADERS)
    def departures():
        for stop in result["data"]["stops"]:
            for departure in stop["stoptimesWithoutPatterns"]:
                yield stop, departure
    return [{
        "destination": parse_headsign(departure["stopHeadsign"]),
        "line": departure["trip"]["route"]["shortName"],
        "realtime": bool(departure["realtime"]),
        "time": parse_time(departure),
        "x": float(stop["lon"]),
        "y": float(stop["lat"]),
    } for stop, departure in departures()]

def find_lines(stops):
    """Return a list of lines that use `stops`."""
    stops = ", ".join('"{}"'.format(x) for x in stops)
    body = format_graphql("find_lines", ids=stops)
    url = URL.format(region=pan.conf.providers.digitransit.region)
    result = pan.http.post_json(url, body, headers=HEADERS)
    def patterns():
        for stop in result["data"]["stops"]:
            for pattern in stop["patterns"]:
                yield pattern
    return sorted_unique_lines([{
        "color": COLORS.get(pattern["route"]["mode"], COLORS["BUS"]),
        "destination": parse_headsign(pattern["headsign"]),
        "id": pattern["route"]["gtfsId"],
        "name": pattern["route"]["shortName"],
    } for pattern in patterns()])

def find_nearby_stops(x, y):
    """Return a list of stops near given coordinates."""
    body = format_graphql("find_nearby_stops", x=x, y=y)
    url = URL.format(region=pan.conf.providers.digitransit.region)
    result = pan.http.post_json(url, body, headers=HEADERS)
    return [{
        "color": get_stop_color(stop),
        "description": stop["desc"] or "",
        "id": stop["gtfsId"],
        "lines": get_stop_lines(stop),
        "name": format_stop_name(stop),
        "x": float(stop["lon"]),
        "y": float(stop["lat"]),
    } for stop in [x["node"]["stop"] for x in
                   result["data"]["stopsByRadius"]["edges"]]]

def find_stops(query, x, y):
    """Return a list of stops matching `query`."""
    query = re.sub('["{}]', "", query)
    body = format_graphql("find_stops", query=query)
    url = URL.format(region=pan.conf.providers.digitransit.region)
    result = pan.http.post_json(url, body, headers=HEADERS)
    return [{
        "color": get_stop_color(stop),
        "description": stop["desc"] or "",
        "id": stop["gtfsId"],
        "lines": get_stop_lines(stop),
        "name": format_stop_name(stop),
        "x": float(stop["lon"]),
        "y": float(stop["lat"]),
    } for stop in result["data"]["stops"]]

@functools.lru_cache(8)
def format_graphql(name, **kwargs):
    """Return GraphQL request body for given request type."""
    directory = os.path.abspath(os.path.dirname(__file__))
    path = "{}/digitransit/{}.graphql".format(directory, name)
    body = open(path, "r").read().strip()
    # Double curly braces to not interfere with str.format.
    body = re.sub(r"\{(\s*)$", r"{{\1", body, flags=re.MULTILINE)
    body = re.sub(r"^(\s*)\}", r"\1}}", body, flags=re.MULTILINE)
    return body.format(**kwargs)

def format_stop_name(stop):
    """Return user visible name for `stop`."""
    name = stop["name"]
    code = stop.get("code", "")
    if not code: return name
    return "{} ({})".format(name, code)

def get_stop_color(stop):
    """Return color to use for `stop` based on modes."""
    modes = [x["route"]["mode"] for x in stop["patterns"]]
    order = ["AIRPLANE", "FERRY", "RAIL", "SUBWAY", "TRAM"]
    order = [x for x in order if x in modes]
    if order: return COLORS[order[0]]
    return COLORS["BUS"]

def get_stop_lines(stop):
    """Return a list of lines that use `stop`."""
    return sorted_unique_lines([{
        "name": pattern["route"]["shortName"],
        "destination": parse_headsign(pattern["headsign"]),
    } for pattern in stop["patterns"]])

def line_to_sort_key(line):
    """Return a key for `line` to use for sorting."""
    # Break into line and modifier, pad with zeros.
    head, tail = line["name"], ""
    while head and head[0].isdigit() and head[-1].isalpha():
        tail = head[-1:] + tail
        head = head[:-1]
    return head.zfill(3), tail.zfill(3)

def parse_headsign(headsign):
    """Return shortened headsign for display."""
    headsign = re.sub(r" via .+$", "", headsign)
    headsign = re.sub(r"(?<! )\(", " (", headsign)
    return headsign

def parse_time(departure):
    """Return Unix time in seconds for `departure`."""
    return int(departure["serviceDay"]) + int(departure["realtimeDeparture"])

def sorted_unique_lines(lines):
    """Return a unique, sorted list of lines."""
    unames = set()
    ulines = [line for line in lines
              if not (line["name"] in unames or unames.add(line["name"]))]
    return sorted(ulines, key=line_to_sort_key)
