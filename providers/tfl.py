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
Public transport stops and departures from Transport for London (TfL).

https://api.tfl.gov.uk/
https://api.tfl.gov.uk/swagger/ui/
https://tfl.gov.uk/plan-a-journey/
"""

import datetime
import functools
import pan
import urllib.parse

COLORS = {
             "bus": "#ed192d",
       "cable-car": "#ed192d",
           "coach": "#ff9900",
             "dlr": "#0fafa9",
   "national-rail": "#ed192d",
      "overground": "#ef6419",
 "replacement-bus": "#ed192d",
       "river-bus": "#289ee0",
      "river-tour": "#289ee0",
         "tflrail": "#244ba6",
            "tram": "#59c134",
            "tube": "#244ba6",
}

# XXX: TfL has stop types in a very complicated hierarchy.
# We should perhaps remove some levels, but I can't tell which.
# For now, just remove stop types that are not mass transit.
IGNORE_STOP_TYPES = [
    "CarPickupSetDownArea",
    "NaptanHailAndRideSection",
    "NaptanSharedTaxi",
    "NaptanTaxiRank",
]

MODE_COLOR_ORDER = [
    "tube",
    "overground",
    "dlr",
    "tflrail",
    "national-rail",
    "tram",
    "cable-car",
    "river-bus",
    "river-tour",
    "coach",
    "replacement-bus",
    "bus",
]

PARAMS = {
    "app_id": "25a1968e",
    "app_key": "57d410a780f5bf0361430f742a1e5189",
}

def find_departures(stops):
    """Return a list of departures from `stops`."""
    if len(stops) > 1:
        return pan.util.sorted_departures(
            find_departures(stops[:1]) +
            find_departures(stops[1:]))
    url = format_url("/StopPoint/{}/Arrivals".format(stops[0]))
    result = pan.http.get_json(url)
    return pan.util.sorted_departures([{
        "destination": departure["towards"],
        "line": departure["lineName"],
        "realtime": False,
        "scheduled_time": parse_time(departure["expectedArrival"]),
        "stop": stops[0],
        "time": parse_time(departure["expectedArrival"]),
    } for departure in result])

def find_lines(stops):
    """Return a list of lines that use `stops`."""
    if len(stops) > 1:
        return pan.util.sorted_unique_lines(
            find_lines(stops[:1]) +
            find_lines(stops[1:]))
    url = format_url("/StopPoint/{}/Route".format(stops[0]))
    result = pan.http.get_json(url)
    return pan.util.sorted_unique_lines([{
        "color": COLORS.get(line["mode"], COLORS["bus"]),
        "destination": line["destinationName"],
        "id": line["naptanId"],
        "name": line["lineId"],
    } for line in result])

def find_nearby_stops(x, y):
    """Return a list of stops near given coordinates."""
    # XXX: Lines are missing destinations.
    # The API endpoint used by find_stops only returns top-levels
    # of stop hierarchies. For consistency with that request
    # stops as a hierarchy and only parse top-levels from that.
    params = dict(stopTypes=",".join(get_stop_types()),
                  radius="500",
                  useStopPointHierarchy="true",
                  categories="none",
                  returnLines="true",
                  lat="{:.6f}".format(y),
                  lon="{:.6f}".format(x))

    url = format_url("/StopPoint", **params)
    result = pan.http.get_json(url)
    return [{
        "color": get_stop_color(stop["modes"]),
        "description": ", ".join(stop["modes"]),
        "id": stop["id"],
        "lines": get_stop_lines(stop),
        "name": stop["commonName"],
        "x": float(stop["lon"]),
        "y": float(stop["lat"]),
    } for stop in result["stopPoints"]]

def find_stops(query, x, y):
    """Return a list of stops matching `query`."""
    # XXX: We cannot seem to get a list of lines without
    # needing to do separate API calls for each stop.
    query = urllib.parse.quote(query)
    path = "/StopPoint/Search/{}".format(query)
    url = format_url(path, maxResults="50")
    result = pan.http.get_json(url)
    return [{
        "color": get_stop_color(match["modes"]),
        "description": ", ".join(match["modes"]),
        "id": match["id"],
        "lines": [],
        "name": match["name"],
        "x": float(match["lon"]),
        "y": float(match["lat"]),
    } for match in result["matches"]]

def format_url(path, **params):
    """Return API URL for `path` with `params`."""
    url = "https://api.tfl.gov.uk{}".format(path)
    params.update(PARAMS)
    params = "&".join("=".join(x) for x in params.items())
    return "?".join((url, params))

def get_stop_color(modes):
    """Return color to use for stop based on `modes`."""
    order = [x for x in MODE_COLOR_ORDER if x in modes]
    if not order: return COLORS["bus"]
    return COLORS.get(order[0], COLORS["bus"])

def get_stop_lines(stop):
    """Return a list of lines that use `stop`."""
    line = lambda x: dict(name=x["name"], destination="")
    return pan.util.sorted_unique_lines(map(line, stop["lines"]))

@functools.lru_cache(1)
def get_stop_types():
    """Return a list of stop types to query for."""
    # XXX: Maybe this doesn't change and we could just save it?
    types = pan.http.get_json(format_url("/StopPoint/Meta/StopTypes"))
    return sorted(set(types) - set(IGNORE_STOP_TYPES))

def parse_time(time):
    """Return Unix time in seconds for `departure`."""
    time = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
    return int(time.timestamp())
