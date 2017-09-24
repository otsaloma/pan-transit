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
import requests
import re
import urllib.parse
import json

baseurl		= "http://ivu.aseag.de/interfaces/ura/{}"
url_l		= "location"
url_i		= "instant_V2"
returnlist	= "StopPointName,StopID,StopPointState,StopPointIndicator,Latitude,Longitude,VisitNumber,TripID,VehicleID,LineID,LineName,DirectionID,DestinationName,DestinationText,EstimatedTime,BaseVersion"

def find_departures(stops):
	#print( "find_dep:"+str(stops[0]) )
	parameter = {'ReturnList': returnlist, 'StopID': ','.join(map(str, stops)) }
	request = requests.get(baseurl.format(url_i), params = parameter)
	if request.status_code != 200:
		raise Exception
	if request.headers['content-type'] != 'application/json;charset=UTF-8':
		raise Exception
	#print(request.text)
	data = parsejson_find_departures(request.text)
	print(data)
	#print("\n\n\n")
	return data

def parsejson_find_departures(data):
	output = []
	for line in data.splitlines():
		linelist = json.loads(line)
		if (linelist[0] == 1):
			output.append({ "destination": linelist[11], "line": linelist[9], "realtime": True, "scheduled_time": linelist[15], "stop": linelist[2], "time": linelist[15], "y": linelist[5], "x": linelist[6] })
	return output

def find_lines(stops):
	"""Return a list of lines that use `stops`."""
	parameter = {'ReturnList': returnlist, 'StopID': ','.join(map(str, stops)) }
	request = requests.get(baseurl.format(url_i), params = parameter)
	if request.status_code != 200:
		raise Exception
	if request.headers['content-type'] != 'application/json;charset=UTF-8':
		raise Exception
	data = parsejson_find_lines(request.text)
	return data

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
	return {"color": "#007ac9", "description": "", "id": "", "line_summary": "", "name": "", "x": 0, "y": 0}

def find_stops(query, x, y):
	parameter = {'searchString': query, 'maxResults': 10, 'searchTypes': 'STOPPOINT'}
	request = requests.get(baseurl.format(url_l), params=parameter)
	if request.status_code != 200:
		raise Exception
	if request.headers['content-type'] != 'application/json;charset=UTF-8':
		raise Exception
	data = parsejson_find_stops(request.json())
	return data

def parsejson_find_stops(data):
	output = []
	data = data['resultList'];
	for line in data:
		output.append({ "color": "#007ac9", "description": line['stopPointName'], "id": line['stopPointId'], "line_summary": "",  "name": line['stopPointName'], 'x': line['longitude'], 'y': line['latitude'] })
	return output
