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
Public transport stops and departures from Aachen, Germany (Aseag).
"""

import pan
import re
import urllib.parse
import json
from operator import itemgetter

baseurl		= "http://ivu.aseag.de/interfaces/ura/{}"
url_l		= "location"
url_i		= "instant_V2"
returnlist	= "StopPointName,StopID,StopPointState,StopPointIndicator,Latitude,Longitude,VisitNumber,TripID,VehicleID,LineID,LineName,DirectionID,DestinationName,DestinationText,EstimatedTime,BaseVersion"

def find_departures(stops):
	parameter = {"ReturnList": returnlist, "StopID": ",".join(map(str, stops)) }
	request = pan.http.get( format_url(baseurl.format(url_i), parameter), encoding="utf_8" )
	data = parsejson_find_departures(request)
	return sorted(data, key=itemgetter("time")) 

def parsejson_find_departures(data):
	output = []
	for line in data.splitlines():
		linelist = json.loads(line)
		if (linelist[0] == 1):
			output.append({ "destination": linelist[11], "line": linelist[9], "realtime": True, "scheduled_time": linelist[15]/1000, "stop": linelist[2], "time": linelist[15]/1000, "y": linelist[5], "x": linelist[6] })
	return output

def find_lines(stops):
	parameter = {"ReturnList": returnlist, "StopID": ",".join(map(str, stops)) }
	request = pan.http.get( format_url(baseurl.format(url_i), parameter), encoding="utf_8" )
	data = parsejson_find_lines(request)
	return sorted(data, key=itemgetter("name")) 

def parsejson_find_lines(data):
	output = []
	for line in data.splitlines():
		linelist = json.loads(line)
		if (linelist[0] == 1):
			newdict = { "destination": linelist[11], "id": linelist[9], "name": linelist[9] }
			if newdict not in output:
				output.append(newdict)
	return output


def find_nearby_stops(x, y):
	return {}

def find_stops(query, x, y):
	parameter = {"searchString": query, "maxResults": "10", "searchTypes": "STOPPOINT"}
	request = pan.http.get_json( format_url(baseurl.format(url_l), parameter), encoding="utf_8" )
	data = parsejson_find_stops(request)
	return data

def parsejson_find_stops(data):
	output = []
	data = data["resultList"]
	for line in data:
		output.append({ "color": "#007ac9", "description": line["stopPointName"], "id": line["stopPointId"], "line_summary": "",  "name": line["stopPointName"], "x": line["longitude"], "y": line["latitude"] })
	return output


def format_url(url, p, **params):
	"""Return API URL for `path` with `params`."""
	params.update(p)
	params = "&".join("=".join(x) for x in params.items())
	return "?".join((url, params))
