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

"""A collection of favorite stop groups and their metadata."""

import copy
import os
import pan
import sys
import threading
import time
import uuid

__all__ = ("Favorites",)


class Favorites:

    """A collection of favorite stop groups and their metadata."""

    def __init__(self):
        """Initialize a :class:`Favorites` instance."""
        self._favorites = []
        self._path = os.path.join(pan.CONFIG_HOME_DIR, "favorites.json")
        self._read()

    def add(self, name):
        """Add `name` as a new favorite and return key."""
        key = str(uuid.uuid4())
        self._favorites.append(pan.AttrDict(key=key,
                                            provider=pan.conf.provider,
                                            name=name,
                                            stops=[],
                                            ignore_lines=[]))

        self._update_meta(key)
        return key

    def add_stop(self, key, props):
        """Add stop to favorite `key`."""
        favorite = self.get(key)
        props = pan.AttrDict(props)
        self.remove_stop(key, props.id)
        favorite.stops.append(pan.AttrDict(id=props.id,
                                           name=props.name,
                                           x=props.x,
                                           y=props.y,
                                           color=props.color))

        self._update_meta(key)

    @property
    def favorites(self):
        """Return a list of favorite stop groups of the current provider."""
        favorites = copy.deepcopy(self._favorites)
        favorites = [x for x in favorites if x.provider == pan.conf.provider]
        favorites.sort(key=lambda x: x.name)
        for favorite in favorites:
            favorite.stops = self.get_stops(favorite.key)
            favorite.color = self.get_color(favorite.key)
            favorite.line_summary = self.get_line_summary(favorite.key)
        return favorites

    def find_departures(self, key):
        """Return a list of departures from favorite `key`."""
        provider = self.get_provider(key)
        if provider is None: return []
        stops = self.get_stop_ids(key)
        ignores = self.get_ignore_lines(key)
        return provider.find_departures(stops, ignores)

    def get(self, key):
        """Return favorite `key` or raise :exc:`LookupError`."""
        for favorite in self._favorites:
            if favorite.key == key:
                return favorite
        raise LookupError("Favorite {} not found"
                          .format(repr(key)))

    def get_color(self, key):
        """Return color to use for favorite `key`."""
        favorite = self.get(key)
        colors = [x.color for x in favorite.stops]
        return pan.util.most_common(colors)

    def get_ignore_lines(self, key):
        """Return a list of lines to not be displayed."""
        favorite = self.get(key)
        return copy.deepcopy(favorite.ignore_lines)

    def get_line_summary(self, key):
        """Return a string listing lines of favorite `key`."""
        favorite = self.get(key)
        lines = favorite.get("lines", [])
        for line in lines:
            line.destination = ""
        lines = pan.util.sorted_unique_lines(lines)
        return ", ".join(x.name for x in lines)

    def get_name(self, key):
        """Return name of favorite `key`."""
        favorite = self.get(key)
        return favorite.name

    def get_provider(self, key):
        """Return provider instance for favorite `key` or ``None``."""
        favorite = self.get(key)
        try:
            return pan.Provider(favorite.provider)
        except Exception as error:
            print("Failed to load provider '{}': {}"
                  .format(favorite.provider, str(error)),
                  file=sys.stderr)
            return None

    def get_stop_ids(self, key):
        """Return a list of stop ids of favorite `key`."""
        return [x.id for x in self.get_stops(key)]

    def get_stops(self, key):
        """Return a list of stops of favorite `key`."""
        favorite = self.get(key)
        stops = copy.deepcopy(favorite.stops)
        return sorted(stops, key=lambda x: x.name)

    def _read(self):
        """Read list of favorites from file."""
        with pan.util.silent(Exception, tb=True):
            if os.path.isfile(self._path):
                self._favorites = list(map(
                    pan.AttrDict,
                    pan.util.read_json(self._path)))
                self._update_meta()

    def remove(self, key):
        """Remove favorite `key` from the list of favorites."""
        keep = lambda x: x.key != key
        self._favorites = list(filter(keep, self._favorites))

    def remove_stop(self, key, id):
        """Remove `id` from stops of favorite `key`."""
        favorite = self.get(key)
        keep = lambda x: x.id != id
        favorite.stops = list(filter(keep, favorite.stops))
        self._update_meta(key)

    def rename(self, key, name):
        """Give favorite `key` a new name."""
        favorite = self.get(key)
        favorite.name = name.strip()

    def set_ignore_lines(self, key, ignore):
        """Set list of lines to not be displayed."""
        favorite = self.get(key)
        favorite.ignore_lines = list(ignore)
        self._update_meta(key)

    def _update_coordinates(self, key):
        """Update favorite coordinates based on stops."""
        favorite = self.get(key)
        sumx = sumy = n = 0
        for stop in favorite.stops:
            with pan.util.silent(Exception):
                sumx += stop.x
                sumy += stop.y
                n += 1
        favorite.x = (sumx/n if n > 0 else 0)
        favorite.y = (sumy/n if n > 0 else 0)

    def _update_lines(self, key, provider):
        """Update list of lines using stops of favorite `key`."""
        with pan.util.silent(Exception, tb=True):
            favorite = self.get(key)
            stops = self.get_stop_ids(key)
            lines = provider.find_lines(stops)
            ignores = self.get_ignore_lines(key)
            lines = pan.util.filter_lines(lines, ignores)
            favorite.lines = list(filter(None, lines))

    def _update_meta(self, *keys):
        """Update metadata, forcing update of favorites `keys`."""
        for key in keys:
            # Force update by marking as old.
            favorite = self.get(key)
            favorite.updated = -1
        for favorite in self._favorites:
            self._update_coordinates(favorite.key)
            # Make sure the first instantiation of a singleton
            # provider happens in the main thread.
            provider = self.get_provider(favorite.key)
            provider.store_stops(favorite.stops)
            if time.time() - favorite.get("updated", -1) > 7 * 86400:
                favorite.updated = int(time.time())
                threading.Thread(target=self._update_lines,
                                 args=[favorite.key, provider],
                                 daemon=True).start()

    def write(self):
        """Write list of favorites to file."""
        with pan.util.silent(Exception, tb=True):
            pan.util.write_json(self._favorites, self._path)
