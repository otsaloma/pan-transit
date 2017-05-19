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

"""Managing a history of search queries."""

import os
import pan

__all__ = ("History",)


class History:

    """Managing a history of search queries."""

    def __init__(self):
        """Initialize a :class:`History` instance."""
        self._queries = []
        self._path = os.path.join(pan.CONFIG_HOME_DIR, "search-history.json")
        self._read()

    def add(self, query):
        """Add `query` to the list of queries."""
        query = query.strip()
        if not query: return
        self.remove(query)
        self._queries.insert(0, query)

    @property
    def queries(self):
        """Return a list of queries."""
        return self._queries[:]

    def _read(self):
        """Read list of queries from file."""
        with pan.util.silent(Exception, tb=True):
            if os.path.isfile(self._path):
                self._queries = pan.util.read_json(self._path)

    def remove(self, query):
        """Remove `query` from the list of queries."""
        query = query.strip().lower()
        keep = lambda x: x.lower() != query
        self._queries = list(filter(keep, self._queries))

    def write(self):
        """Write list of queries to file."""
        with pan.util.silent(Exception, tb=True):
            pan.util.write_json(self._queries[:1000], self._path)
