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

"""Departures from public transportation stops."""

__version__ = "1.1"

try:
    import pyotherside
except ImportError:
    import sys
    # Allow testing Python backend alone.
    print("PyOtherSide not found, continuing anyway!",
          file=sys.stderr)
    class pyotherside:
        def atexit(*args): pass
        def send(*args): pass
    sys.modules["pyotherside"] = pyotherside()

from pan.paths import CACHE_HOME_DIR
from pan.paths import CONFIG_HOME_DIR
from pan.paths import DATA_DIR
from pan.paths import DATA_HOME_DIR
from pan.paths import LOCALE_DIR
from pan import i18n
from pan import util
from pan import http
from pan.attrdict import AttrDict
from pan.provider import Provider
from pan.favorites import Favorites
from pan.history import History
from pan.config import ConfigurationStore
conf = ConfigurationStore()
from pan.application import Application

assert Application
assert AttrDict
assert CACHE_HOME_DIR
assert CONFIG_HOME_DIR
assert ConfigurationStore
assert DATA_DIR
assert DATA_HOME_DIR
assert Favorites
assert History
assert http
assert i18n
assert LOCALE_DIR
assert Provider
assert util

def main():
    """Initialize application."""
    conf.read()
    global app
    app = Application()
