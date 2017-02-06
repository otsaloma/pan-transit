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

"""Miscellaneous helper functions."""

import collections
import contextlib
import copy
import functools
import glob
import json
import locale
import math
import os
import pan
import random
import re
import shutil
import socket
import stat
import sys
import time
import traceback
import urllib.parse

from pan.i18n import _


def api_query(fallback):
    """Decorator for API requests with graceful error handling."""
    def outer_wrapper(function):
        @functools.wraps(function)
        def inner_wrapper(*args, **kwargs):
            try:
                # function can fail due to connection errors or errors
                # in parsing the received data. Notify the user of some
                # common errors by returning a dictionary with the error
                # message to be displayed. With unexpected errors, print
                # a traceback and return blank of correct type.
                return function(*args, **kwargs)
            except socket.timeout:
                return dict(error=True, message=_("Connection timed out"))
            except Exception:
                traceback.print_exc()
                return copy.deepcopy(fallback)
        return inner_wrapper
    return outer_wrapper

@contextlib.contextmanager
def atomic_open(path, mode="w", *args, **kwargs):
    """A context manager for atomically writing a file."""
    # This is a simplified version of atomic_open from gaupol.
    # https://github.com/otsaloma/gaupol/blob/master/aeidon/util.py
    path = os.path.realpath(path)
    suffix = random.randint(1, 10**9)
    temp_path = "{}.tmp{}".format(path, suffix)
    try:
        if os.path.isfile(path):
            # If the file exists, use the same permissions.
            # Note that all other file metadata, including
            # owner and group, is not preserved.
            with open(temp_path, "w") as f: pass
            st = os.stat(path)
            os.chmod(temp_path, stat.S_IMODE(st.st_mode))
        with open(temp_path, mode, *args, **kwargs) as f:
            yield f
            f.flush()
            os.fsync(f.fileno())
        try:
            # Requires Python 3.3 or later.
            # Can fail in the unlikely case that
            # paths are on different filesystems.
            os.replace(temp_path, path)
        except OSError:
            # Fall back on a non-atomic operation.
            shutil.move(temp_path, path)
    finally:
        with silent(Exception):
            os.remove(temp_path)

def calculate_distance(x1, y1, x2, y2):
    """Calculate distance in meters from point 1 to point 2."""
    # Using the haversine formula.
    # http://www.movable-type.co.uk/scripts/latlong.html
    x1, y1, x2, y2 = map(math.radians, (x1, y1, x2, y2))
    a = (math.sin((y2-y1)/2)**2 +
         math.sin((x2-x1)/2)**2 * math.cos(y1) * math.cos(y2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return 6371000 * c

def departure_time_to_color(dist, departure):
    """
    Return color to use for departure based on time and distance remaining.

    `dist` should be straight-line distance to stop in meters and
    `departure` should be the Unix time of departure.
    """
    # Actual walking distance is usually between 1 and 1.414,
    # on average maybe around 1.2, times the straight-line distance.
    # We can bump that figure a bit to account for traffic lights etc.
    dist = 1.35 * dist
    min_left = (departure - time.time()) / 60
    # Use walking speeds from reittiopas.fi:
    # 70 m/min for normal and 100 m/min for fast speed.
    if min_left > 3 and dist /  70 <= min_left: return "#3890ff"
    if min_left > 1 and dist / 100 <= min_left: return "#fff444"
    return "#ff4744"

def format_departure_time(departure):
    """Format Unix time `departure` for display."""
    min_left = (departure - time.time()) / 60
    if min_left < -1.5:
        return ""
    # Use minutes if below defined threshold,
    # otherwise time as HH:MM.
    if min_left < max((0, pan.conf.departure_time_cutoff)):
        return "{:d} min".format(math.floor(min_left))
    departure = time.localtime(departure)
    return "{:.0f}:{:02.0f}".format(departure.tm_hour,
                                    departure.tm_min)

def format_distance(meters, n=2):
    """Format `meters` to `n` significant digits and unit label."""
    if pan.conf.units == "american":
        feet = 3.28084 * meters
        return format_distance_american(feet, n)
    if pan.conf.units == "british":
        yards = 1.09361 * meters
        return format_distance_british(yards, n)
    return format_distance_metric(meters, n)

def format_distance_american(feet, n=2):
    """Format `feet` to `n` significant digits and unit label."""
    if (n > 1 and feet >= 1000) or feet >= 5280:
        distance = feet/5280
        units = "mi"
    else:
        # Let's not use units less than a foot.
        distance = feet
        units = "ft"
    ndigits = n - math.ceil(math.log10(abs(max(1, distance)) + 1/1000000))
    if units == "ft":
        ndigits = min(0, ndigits)
    distance = round(distance, ndigits)
    fstring = "{{:.{:d}f}} {{}}".format(max(0, ndigits))
    return fstring.format(distance, units)

def format_distance_british(yards, n=2):
    """Format `yards` to `n` significant digits and unit label."""
    if (n > 1 and yards >= 400) or yards >= 1760:
        distance = yards/1760
        units = "mi"
    else:
        # Let's not use units less than a yard.
        distance = yards
        units = "yd"
    ndigits = n - math.ceil(math.log10(abs(max(1, distance)) + 1/1000000))
    if units == "yd":
        ndigits = min(0, ndigits)
    distance = round(distance, ndigits)
    fstring = "{{:.{:d}f}} {{}}".format(max(0, ndigits))
    return fstring.format(distance, units)

def format_distance_metric(meters, n=2):
    """Format `meters` to `n` significant digits and unit label."""
    if meters >= 1000:
        distance = meters/1000
        units = "km"
    else:
        # Let's not use units less than a meter.
        distance = meters
        units = "m"
    ndigits = n - math.ceil(math.log10(abs(max(1, distance)) + 1/1000000))
    if units == "m":
        ndigits = min(0, ndigits)
    distance = round(distance, ndigits)
    fstring = "{{:.{:d}f}} {{}}".format(max(0, ndigits))
    return fstring.format(distance, units)

def get_default_language(fallback="en"):
    """Return the system default language code or `fallback`."""
    return (locale.getdefaultlocale()[0] or fallback)[:2]

def get_default_locale(fallback="en_US"):
    """Return the system default locale code or `fallback`."""
    return (locale.getdefaultlocale()[0] or fallback)[:5]

def get_providers():
    """Return a list of dictionaries of provider attributes."""
    providers = []
    for parent in (pan.DATA_HOME_DIR, pan.DATA_DIR):
        for path in glob.glob("{}/providers/*.json".format(parent)):
            pid = os.path.basename(path).replace(".json", "")
            # Local definitions override global ones.
            if pid in (x["pid"] for x in providers): continue
            provider = read_json(path)
            provider["pid"] = pid
            provider["active"] = (pid == pan.conf.provider)
            providers.append(provider)
    providers.sort(key=lambda x: x["name"])
    return providers

def line_to_sort_key(line):
    """Return a key for `line` to use for sorting."""
    line = re.sub(r"\W", "", line.upper())
    if not line:
        return line_to_sort_key("0")
    alpha = re.match("^([A-Z]+)(.*)$", line)
    digit = re.match("^([0-9]+)(.*)$", line)
    if alpha is not None:
        head, tail = alpha.group(1), alpha.group(2)
        return head, tail.zfill(100)
    if digit is not None:
        head, tail = digit.group(1), digit.group(2)
        return head.zfill(100), tail
    raise ValueError("Bad line: {}".format(repr(line)))

def locked_method(function):
    """
    Decorator for methods to be run thread-safe.

    Requires class to have an instance variable '_lock'.
    """
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        with args[0]._lock:
            return function(*args, **kwargs)
    return wrapper

def makedirs(directory):
    """Create and return `directory` or raise :exc:`OSError`."""
    directory = os.path.abspath(directory)
    if os.path.isdir(directory):
        return directory
    try:
        os.makedirs(directory)
    except OSError as error:
        if os.path.isdir(directory):
            return directory
        print("Failed to create directory {}: {}"
              .format(repr(directory), str(error)),
              file=sys.stderr)
        raise # OSError
    return directory

def most_common(seq):
    """Return the most common value in `seq`."""
    # Counter orders ties arbitrarily, we want the same value
    # on each call, let that be the one sorted first.
    if not seq: return None
    counts = collections.Counter(seq).most_common()
    values = [value for value, count in counts if count == counts[0][1]]
    return sorted(values)[0]

def path2uri(path):
    """Convert local filepath to URI."""
    return "file://{}".format(urllib.parse.quote(path))

def read_json(path):
    """Read data from JSON file at `path`."""
    try:
        with open(path, "r", encoding="utf_8") as f:
            data = json.load(f)
    except Exception as error:
        print("Failed to read file {}: {}"
              .format(repr(path), str(error)),
              file=sys.stderr)
        raise # Exception
    # Translatable field names are prefixed with an underscore,
    # e.g. "_description". Translate the values of these fields
    # and drop the underscore from the field name.
    def translate(value):
        if isinstance(value, list):
            return list(map(translate, value))
        return _(value)
    if isinstance(data, dict):
        for key in [x for x in data if x.startswith("_")]:
            data[key[1:]] = translate(data.pop(key))
    return data

@contextlib.contextmanager
def silent(*exceptions, tb=False):
    """Try to execute body, ignoring `exceptions`."""
    try:
        yield
    except exceptions:
        if tb: traceback.print_exc()

def sorted_by_distance(items, x, y):
    """Return `items` sorted by distance from given coordinates."""
    for item in items:
        item["__dist"] = calculate_distance(item["x"], item["y"], x, y)
    items = sorted(items, key=lambda z: z["__dist"])
    for item in items:
        del item["__dist"]
    return items

def sorted_departures(departures):
    """Return `departures` sorted by time and line."""
    return sorted(departures, key=lambda x:
                  (x["time"], line_to_sort_key(x["line"])))

def sorted_unique_lines(lines):
    """Return a unique, sorted list of lines."""
    unames = set()
    ulines = [line for line in lines
              if not (line["name"] in unames or unames.add(line["name"]))]
    return sorted(ulines, key=lambda x: line_to_sort_key(x["name"]))

def write_json(data, path):
    """Write `data` to JSON file at `path`."""
    try:
        makedirs(os.path.dirname(path))
        with atomic_open(path, "w", encoding="utf_8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=True)
    except Exception as error:
        print("Failed to write file {}: {}"
              .format(repr(path), str(error)),
              file=sys.stderr)
        raise # Exception
