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

"""Departures from public transport stops."""

__all__ = ("Application",)

import pan
import sys


class Application:

    """Departures from public transport stops."""

    def __init__(self):
        """Initialize an :class:`Application` instance."""
        self.favorites = pan.Favorites()
        self.history = pan.History()
        self.provider = None
        self.set_provider(pan.conf.provider)

    def quit(self):
        """Quit the application."""
        pan.http.pool.terminate()
        self.save()

    def save(self):
        """Write configuration files."""
        pan.conf.write()
        self.favorites.write()
        self.history.write()

    def set_provider(self, provider):
        """Set provider from string `provider`."""
        try:
            self.provider = pan.Provider(provider)
            pan.conf.provider = provider
        except Exception as error:
            print("Failed to load provider '{}': {}"
                  .format(provider, str(error)),
                  file=sys.stderr)
            if self.provider is None:
                default = pan.conf.get_default("provider")
                if default != provider:
                    self.set_provider(default)
