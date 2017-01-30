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
        pan.conf.set("items", [1,2,3])
        assert pan.conf.items == [1,2,3]
        pan.conf.add("items", 4)
        assert pan.conf.items == [1,2,3,4]

    def test_contains(self):
        pan.conf.set("items", [1,2,3])
        assert pan.conf.items == [1,2,3]
        assert pan.conf.contains("items", 1)
        assert not pan.conf.contains("items", 4)

    def test_get(self):
        assert pan.conf.get("units") == "metric"

    def test_get_default(self):
        assert pan.conf.get_default("units") == "metric"

    def test_get_default__nested(self):
        pan.config.DEFAULTS["foo"] = pan.config.AttrDict()
        pan.config.DEFAULTS["foo"]["bar"] = 1
        assert pan.conf.get_default("foo.bar") == 1

    def test_read(self):
        pan.conf.units = "american"
        pan.conf.write(self.path)
        pan.conf.clear()
        assert not pan.conf
        pan.conf.read(self.path)
        assert pan.conf.units == "american"

    def test_read__nested(self):
        pan.conf.register_provider("foo", {"type": 1})
        pan.conf.write(self.path)
        del pan.conf.providers["foo"]
        assert not "foo" in pan.conf.providers
        pan.conf.read(self.path)
        assert pan.conf.providers.foo.type == 1

    def test_register_provider(self):
        pan.conf.register_provider("foo", {"type": 1})
        assert pan.conf.providers.foo.type == 1
        assert pan.conf.get_default("providers.foo.type") == 1

    def test_register_provider__again(self):
        # Subsequent calls should not change values.
        pan.conf.register_provider("foo", {"type": 1})
        pan.conf.providers.foo.type = 2
        pan.conf.register_provider("foo", {"type": 1})
        assert pan.conf.providers.foo.type == 2
        assert pan.conf.get_default("providers.foo.type") == 1

    def test_remove(self):
        pan.conf.set("items", [1,2,3])
        assert pan.conf.items == [1,2,3]
        pan.conf.remove("items", 3)
        assert pan.conf.items == [1,2]

    def test_set(self):
        pan.conf.set("units", "american")
        assert pan.conf.units == "american"

    def test_set__nested(self):
        pan.conf.set("foo.bar", 1)
        assert pan.conf.foo.bar == 1

    def test_write(self):
        pan.conf.units = "american"
        pan.conf.write(self.path)
        pan.conf.clear()
        assert not pan.conf
        pan.conf.read(self.path)
        assert pan.conf.units == "american"
