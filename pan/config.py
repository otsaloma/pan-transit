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

"""Attribute dictionary of configuration values."""

import copy
import os
import pan
import sys

__all__ = ("ConfigurationStore",)

DEFAULTS = {
    "departure_time_cutoff": 10,
    "favorite_highlight_radius": 1000,
    "provider": "digitransit_hsl",
    "units": "metric",
}


class ConfigurationStore(pan.AttrDict):

    """Attribute dictionary of configuration values."""

    def __init__(self):
        """Initialize a :class:`Configuration` instance."""
        pan.AttrDict.__init__(self, copy.deepcopy(DEFAULTS))

    def add(self, option, item):
        """Add `item` to the value of `option`."""
        root, name = self._split_option(option)
        if item in root[name]: return
        root[name].append(copy.deepcopy(item))

    def _coerce(self, value, ref):
        """Coerce type of `value` to match `ref`."""
        if isinstance(value, list) and ref:
            return [self._coerce(x, ref[0]) for x in value]
        return type(ref)(value)

    def contains(self, option, item):
        """Return ``True`` if the value of `option` contains `item`."""
        root, name = self._split_option(option)
        return item in root[name]

    def get(self, option):
        """Return the value of `option`."""
        root = self
        for section in option.split(".")[:-1]:
            root = root[section]
        name = option.split(".")[-1]
        return copy.deepcopy(root[name])

    def get_default(self, option):
        """Return the default value of `option`."""
        root = DEFAULTS
        for section in option.split(".")[:-1]:
            root = root[section]
        name = option.split(".")[-1]
        return copy.deepcopy(root[name])

    def read(self, path=None):
        """Read values of options from JSON file at `path`."""
        path = path or os.path.join(pan.CONFIG_HOME_DIR, "pan-transit.json")
        if not os.path.isfile(path): return
        values = {}
        with pan.util.silent(Exception, tb=True):
            values = pan.util.read_json(path)
        self._update(values)

    def remove(self, option, item):
        """Remove `item` from the value of `option`."""
        root, name = self._split_option(option)
        if not item in root[name]: return
        root[name].remove(item)

    def set(self, option, value):
        """Set the value of `option`."""
        root, name = self._split_option(option, create=True)
        with pan.util.silent(Exception):
            value = self._coerce(value, self.get_default(option))
        root[name] = copy.deepcopy(value)

    def _split_option(self, option, create=False):
        """Split dotted option to dictionary and option name."""
        root = self
        for section in option.split(".")[:-1]:
            if create and not section in root:
                # Create missing hierarchies.
                root[section] = pan.AttrDict()
            root = root[section]
        name = option.split(".")[-1]
        return root, name

    def _update(self, values, root=None, defaults=None, path=()):
        """Load values of options after validation."""
        if root is None: root = self
        if defaults is None: defaults = DEFAULTS
        for name, value in values.items():
            if isinstance(value, dict):
                self._update(value,
                             root.setdefault(name, pan.AttrDict()),
                             defaults.setdefault(name, {}),
                             path + (name,))
                continue
            try:
                if name in defaults:
                    # Be liberal, but careful in what to accept.
                    value = self._coerce(value, defaults[name])
                root[name] = copy.deepcopy(value)
            except Exception as error:
                full_name = ".".join(path + (name,))
                print("Discarding bad option-value pair {}, {}: {}"
                      .format(repr(full_name), repr(value), str(error)),
                      file=sys.stderr)

    def write(self, path=None):
        """Write values of options to JSON file at `path`."""
        path = path or os.path.join(pan.CONFIG_HOME_DIR, "pan-transit.json")
        out = copy.deepcopy(self)
        # Make sure no obsolete top-level options remain.
        names = list(DEFAULTS.keys())
        for name in list(out.keys()):
            if not name in names:
                del out[name]
        out["version"] = pan.__version__
        with pan.util.silent(Exception, tb=True):
            pan.util.write_json(out, path)
