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


class TestHistory(pan.test.TestCase):

    def setup_method(self, method):
        self.history = pan.History()

    def test_add(self):
        self.history.add("test")
        assert self.history.queries[0] == "test"

    def test_queries(self):
        self.history.add("test")
        assert self.history.queries

    def test_remove(self):
        self.history.add("test")
        assert self.history.queries[0] == "test"
        self.history.remove("test")
        assert not self.history.queries
