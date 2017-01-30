/* -*- coding: utf-8-unix -*-
 *
 * Copyright (C) 2014 Osmo Salomaa
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick 2.0
import Sailfish.Silica 1.0

Column {
    ComboBox {
        id: regionComboBox
        label: qsTranslate("", "Region")
        menu: ContextMenu {
            MenuItem { text: qsTranslate("", "HSL") }
            MenuItem { text: qsTranslate("", "Waltti") }
            MenuItem { text: qsTranslate("", "Finland") }
        }
        property var keys: ["hsl", "waltti", "finland"]
        Component.onCompleted: {
            var key = app.conf.get("providers.digitransit.region");
            regionComboBox.currentIndex = regionComboBox.keys.indexOf(key);
        }
        onCurrentIndexChanged: {
            var key = regionComboBox.keys[regionComboBox.currentIndex];
            app.conf.set("providers.digitransit.region", key);
        }
    }
}
