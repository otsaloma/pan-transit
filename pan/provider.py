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

"""A proxy for information from providers."""

import importlib.machinery
import os
import pan
import random
import re

__all__ = ("Provider",)


class Provider:

    """A proxy for information from providers."""

    def __new__(cls, id):
        """Return possibly existing instance for `id`."""
        if not hasattr(cls, "_instances"):
            cls._instances = {}
        if not id in cls._instances:
            cls._instances[id] = object.__new__(cls)
        return cls._instances[id]

    def __init__(self, id):
        """Initialize a :class:`Provider` instance."""
        # Initialize properties only once.
        if hasattr(self, "id"): return
        path, values = self._load_attributes(id)
        self.description = values["description"]
        self.id = id
        self.name = values["name"]
        self._path = path
        self._provider = None
        self.update_interval = int(values["update_interval"])
        self._init_provider(id, re.sub(r"\.json$", ".py", path))

    @pan.util.api_query([])
    def find_departures(self, stops):
        """Return a list of departures from `stops`."""
        if not stops: return []
        return self._provider.find_departures(stops)

    @pan.util.api_query([])
    def find_lines(self, stops):
        """Return a list of lines that use `stops`."""
        if not stops: return []
        return self._provider.find_lines(stops)

    @pan.util.api_query([])
    def find_nearby_stops(self, x, y):
        """Return a list of stops near given coordinates."""
        stops = self._provider.find_nearby_stops(x, y)
        stops = pan.util.sorted_by_distance(stops, x, y)
        for stop in stops:
            dist = pan.util.calculate_distance(x, y, stop["x"], stop["y"])
            stop["dist"] = pan.util.format_distance(dist)
        return stops

    @pan.util.api_query([])
    def find_stops(self, query, x, y):
        """Return a list of stops matching `query`."""
        if not query: return []
        stops = self._provider.find_stops(query, x, y)
        for stop in stops:
            dist = pan.util.calculate_distance(x, y, stop["x"], stop["y"])
            stop["dist"] = pan.util.format_distance(dist)
        return stops

    def _init_provider(self, id, path):
        """Initialize transit provider module from `path`."""
        name = "pan.provider{:d}".format(random.randrange(10**12))
        loader = importlib.machinery.SourceFileLoader(name, path)
        self._provider = loader.load_module(name)
        if hasattr(self._provider, "CONF_DEFAULTS"):
            pan.conf.register_provider(id, self._provider.CONF_DEFAULTS)

    def _load_attributes(self, id):
        """Read and return attributes from JSON file."""
        leaf = os.path.join("providers", "{}.json".format(id))
        path = os.path.join(pan.DATA_HOME_DIR, leaf)
        if not os.path.isfile(path):
            path = os.path.join(pan.DATA_DIR, leaf)
        return path, pan.util.read_json(path)

    @property
    def settings_qml_uri(self):
        """Return URI to router settings QML file or ``None``."""
        path = re.sub(r"\.json$", "_settings.qml", self._path)
        if not os.path.isfile(path): return None
        return pan.util.path2uri(path)
