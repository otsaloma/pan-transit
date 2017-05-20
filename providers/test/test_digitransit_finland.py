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

import pan.test


class TestModule(pan.test.TestCase):

    def setup_method(self, method):
        self.provider = pan.Provider("digitransit_finland")

    def test_find_departures(self):
        stops = ["MATKA:300340", "MATKA:310513"]
        departures = self.provider.find_departures(stops)
        departures = list(map(pan.AttrDict, departures))
        assert departures
        for departure in departures:
            assert departure.destination
            assert departure.line
            assert departure.stop
            assert departure.time
            assert departure.x
            assert departure.y

    def test_find_lines(self):
        stops = ["MATKA:300340", "MATKA:310513"]
        lines = self.provider.find_lines(stops)
        lines = list(map(pan.AttrDict, lines))
        assert lines
        for line in lines:
            assert line.color
            assert line.destination
            assert line.id
            assert line.name

    def test_find_nearby_stops(self):
        stops = self.provider.find_nearby_stops(27.273, 61.689)
        stops = list(map(pan.AttrDict, stops))
        assert stops
        for stop in stops:
            assert stop.color
            assert stop.id
            assert stop.line_summary
            assert stop.name
            assert stop.x
            assert stop.y

    def test_find_stops(self):
        stops = self.provider.find_stops("raatihuone", 27.273, 61.689)
        stops = list(map(pan.AttrDict, stops))
        assert stops
        for stop in stops:
            assert stop.color
            assert stop.id
            assert stop.line_summary
            assert stop.name
            assert stop.x
            assert stop.y
