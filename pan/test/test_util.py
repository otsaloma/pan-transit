# -*- coding: utf-8 -*-

# Copyright (C) 2014 Osmo Salomaa
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

import os
import pan.test
import tempfile


class TestModule(pan.test.TestCase):

    def test_atomic_open__file_exists(self):
        text = "testing\ntesting\n"
        handle, path = tempfile.mkstemp()
        with pan.util.atomic_open(path, "w") as f:
            f.write(text)
        assert open(path, "r").read() == text
        os.remove(path)

    def test_atomic_open__new_file(self):
        text = "testing\ntesting\n"
        handle, path = tempfile.mkstemp()
        os.remove(path)
        with pan.util.atomic_open(path, "w") as f:
            f.write(text)
        assert open(path, "r").read() == text
        os.remove(path)

    def test_calculate_distance(self):
        # From Helsinki to Lissabon.
        dist = pan.util.calculate_distance(24.94, 60.17, -9.14, 38.72)
        assert round(dist/1000) == 3361

    def test_filter_departures(self):
        a = dict(line="a", destination="aaa")
        b = dict(line="b", destination="bbb")
        ignores = [dict(name="B", destination="BBB")]
        value = pan.util.filter_departures([a, b], ignores)
        assert value == [a]

    def test_filter_lines(self):
        a = dict(name="a", destination="aaa")
        b = dict(name="b", destination="bbb")
        ignores = [dict(name="B", destination="BBB")]
        value = pan.util.filter_lines([a, b], ignores)
        assert value == [a]

    def test_format_distance_american(self):
        assert pan.util.format_distance_american(123, 2) == "120 ft"
        assert pan.util.format_distance_american(6000, 1) == "1 mi"

    def test_format_distance_british(self):
        assert pan.util.format_distance_british(123, 2) == "120 yd"
        assert pan.util.format_distance_british(2000, 1) == "1 mi"

    def test_format_distance_metric(self):
        assert pan.util.format_distance_metric(123, 2) == "120 m"
        assert pan.util.format_distance_metric(1234, 1) == "1 km"

    def test_line_to_sort_key__1(self):
        key = pan.util.line_to_sort_key
        lines = ["58", "58B", "506"]
        assert sorted(lines[::-1], key=key) == lines

    def test_line_to_sort_key__2(self):
        key = pan.util.line_to_sort_key
        lines = ["A", "A1", "AA", "AAA", "B"]
        assert sorted(lines[::-1], key=key) == lines

    def test_line_to_sort_key__3(self):
        key = pan.util.line_to_sort_key
        lines = ["Arles", "Bordeaux 11", "Bordeaux 12", "Cannes"]
        assert sorted(lines[::-1], key=key) == lines

    def test_most_common(self):
        assert pan.util.most_common([1,1,1,2,2,3]) == 1
        assert pan.util.most_common([2,2,1,1]) == 1

    def test_sorted_unique_lines(self):
        lines = ["10", "103", "103", "102", "102T", "102T"]
        lines = [dict(name=x, destination="") for x in lines]
        ulines = pan.util.sorted_unique_lines(lines)
        ulines = [x["name"] for x in ulines]
        assert ulines == ["10", "102", "102T", "103"]
