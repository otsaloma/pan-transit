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
import pan
import re
import urllib.parse

COLORS = pan.AttrDict({
             "bus": "#ed192d",
       "cable-car": "#ed192d",
           "coach": "#ed192d",
             "dlr": "#244ba6",
   "national-rail": "#244ba6",
      "overground": "#244ba6",
 "replacement-bus": "#ed192d",
       "river-bus": "#289ee0",
      "river-tour": "#289ee0",
         "tflrail": "#244ba6",
            "tram": "#59c134",
            "tube": "#244ba6",
})

DESTINATION_SUFFIXES = [
    "dlr station",
    "rail station",
    "tram stop",
    "underground station",
]

MODE_COLOR_ORDER = [
    "national-rail",
    "tflrail",
    "dlr",
    "tube",
    "overground",
    "tram",
    "river-bus",
    "river-tour",
    "cable-car",
    "coach",
    "replacement-bus",
    "bus",
]

PARAMS = {
    "app_id": "25a1968e",
    "app_key": "57d410a780f5bf0361430f742a1e5189",
}

# Full list of stop types is available from the API. There's a lot of
# stop types and they form a confusing hierarchy and not all of them
# even work. Based on some experimentation, it seems the below short list
# would be enough and would keep non-functional results to a minimum.
# https://api.tfl.gov.uk/StopPoint/Meta/StopType
STOP_TYPES = [
    "NaptanFerryPort",
    "NaptanMetroStation",
    "NaptanPublicBusCoachTram",
    "NaptanRailStation",
]

def find_departures(stops):
    """Return a list of departures from `stops`."""
    if len(stops) > 1:
        return pan.util.sorted_departures(
            find_departures(stops[:1]) +
            find_departures(stops[1:]))
    url = format_url("/StopPoint/{}/Arrivals".format(stops[0]))
    result = pan.http.get_json(url)
    result = list(map(pan.AttrDict, result))
    return pan.util.sorted_departures([{
        "destination": parse_destination(
            departure.get("destinationName", "") or
            departure.get("towards", "")),
        "line": departure.lineName,
        "realtime": False,
        "scheduled_time": parse_time(departure.expectedArrival),
        "stop": stops[0],
        "time": parse_time(departure.expectedArrival),
    } for departure in result])

def find_lines(stops):
    """Return a list of lines that use `stops`."""
    if len(stops) > 1:
        return pan.util.sorted_unique_lines(
            find_lines(stops[:1]) +
            find_lines(stops[1:]))
    url = format_url("/StopPoint/{}/Route".format(stops[0]))
    result = pan.http.get_json(url)
    result = list(map(pan.AttrDict, result))
    return pan.util.sorted_unique_lines([{
        "color": COLORS.get(line.mode, COLORS.bus),
        "destination": parse_destination(line.destinationName),
        "id": line.naptanId,
        "name": line.lineId,
    } for line in result])

def find_nearby_stops(x, y):
    """Return a list of stops near given coordinates."""
    # XXX: The API endpoint used by find_stops doesn't require
    # a stopTypes argument, but returns sensibly filtered results.
    # We try to match that, but don't quite succeed.
    params = dict(stopTypes=",".join(STOP_TYPES),
                  radius="500",
                  useStopPointHierarchy="false",
                  categories="none",
                  returnLines="true",
                  lat="{:.6f}".format(y),
                  lon="{:.6f}".format(x))

    url = format_url("/StopPoint", **params)
    result = pan.http.get_json(url)
    result = pan.AttrDict(result)
    return [{
        "color": get_stop_color(stop.modes),
        "description": get_stop_description(stop),
        "id": stop.id,
        "line_summary": get_line_summary(stop),
        "name": stop.commonName,
        "x": float(stop.lon),
        "y": float(stop.lat),
    } for stop in result.stopPoints]

def find_stops(query, x, y):
    """Return a list of stops matching `query`."""
    # XXX: We cannot seem to get a list of lines without
    # needing to do separate API calls for each stop.
    query = urllib.parse.quote(query)
    path = "/StopPoint/Search/{}".format(query)
    url = format_url(path, maxResults="50", includeHubs="false")
    result = pan.http.get_json(url)
    result = pan.AttrDict(result)
    return [{
        "color": get_stop_color(match.modes),
        "description": get_stop_description(match),
        "id": match.id,
        "line_summary": "",
        "name": match.name,
        "x": float(match.lon),
        "y": float(match.lat),
    } for match in result.matches]

def format_url(path, **params):
    """Return API URL for `path` with `params`."""
    url = "https://api.tfl.gov.uk{}".format(path)
    params.update(PARAMS)
    params = "&".join("=".join(x) for x in params.items())
    return "?".join((url, params))

def get_line_summary(stop):
    """Return a list of lines that use `stop`."""
    line = lambda x: pan.AttrDict(name=x.name, destination="")
    lines = pan.util.sorted_unique_lines(map(line, stop.lines))
    return ", ".join(x.name for x in lines[:10])

def get_stop_color(modes):
    """Return color to use for stop based on `modes`."""
    order = [x for x in MODE_COLOR_ORDER if x in modes]
    if not order: return COLORS.bus
    return COLORS.get(order[0], COLORS.bus)

def get_stop_description(stop):
    """Return description to use for stop."""
    modes = stop.get("modes", "") or "—"
    indicator = stop.get("indicator", "")
    if not indicator: return ", ".join(modes)
    return " · ".join((", ".join(modes), indicator))

def parse_destination(destination):
    """Return `destination` with possible suffixes removed."""
    # Some API endpoints include these suffixes, others don't.
    # To be able to do line filtering correctly we need consistency.
    for suffix in DESTINATION_SUFFIXES:
        pattern = " +{}$".format(suffix)
        destination = re.sub(pattern, "", destination, flags=re.I)
    return destination.strip()

def parse_time(time):
    """Return Unix time in seconds for `departure`."""
    time = "{}+0000".format(time)
    time = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ%z")
    return int(time.timestamp())
