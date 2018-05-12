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

import imp
import os
import pan.test
import tempfile


class TestConfigurationStore(pan.test.TestCase):

    def setup_method(self, method):
        imp.reload(pan.config)
        pan.conf = pan.ConfigurationStore()
        handle, self.path = tempfile.mkstemp()

    def teardown_method(self, method):
        os.remove(self.path)

    def test_add(self):
        pan.conf.set("test", [1, 2, 3])
        assert pan.conf.test == [1, 2, 3]
        pan.conf.add("test", 4)
        assert pan.conf.test == [1, 2, 3, 4]

    def test_contains(self):
        pan.conf.set("test", [1, 2, 3])
        assert pan.conf.test == [1, 2, 3]
        assert pan.conf.contains("test", 1)
        assert not pan.conf.contains("test", 4)

    def test_get(self):
        assert pan.conf.get("provider") == "digitransit_hsl"

    def test_get_default(self):
        assert pan.conf.get_default("provider") == "digitransit_hsl"

    def test_get_default__nested(self):
        pan.config.DEFAULTS["foo"] = dict(bar=1)
        assert pan.conf.get_default("foo.bar") == 1

    def test_read(self):
        pan.conf.provider = "foo"
        pan.conf.write(self.path)
        pan.conf.clear()
        assert not pan.conf
        pan.conf.read(self.path)
        assert pan.conf.provider == "foo"

    def test_read__nested(self):
        pan.config.DEFAULTS["foo"] = dict(bar=1)
        pan.conf.set("foo.bar", 2)
        pan.conf.write(self.path)
        del pan.conf.foo
        assert not "foo" in pan.conf
        pan.conf.read(self.path)
        assert pan.conf.foo.bar == 2

    def test_remove(self):
        pan.conf.set("test", [1, 2, 3])
        assert pan.conf.test == [1, 2, 3]
        pan.conf.remove("test", 3)
        assert pan.conf.test == [1, 2]

    def test_set(self):
        pan.conf.set("provider", "foo")
        assert pan.conf.provider == "foo"

    def test_set__coerce(self):
        pan.conf.set("departure_time_cutoff", 10.1)
        assert pan.conf.departure_time_cutoff == 10

    def test_set__nested(self):
        pan.conf.set("foo.bar", 1)
        assert pan.conf.foo.bar == 1

    def test_write(self):
        pan.conf.provider = "foo"
        pan.conf.write(self.path)
        pan.conf.clear()
        assert not pan.conf
        pan.conf.read(self.path)
        assert pan.conf.provider == "foo"
