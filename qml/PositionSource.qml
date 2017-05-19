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
import QtPositioning 5.2

PositionSource {
    id: gps
    active: app.applicationActive
    updateInterval: 1000

    property bool ready: false

    onPositionChanged: {
        // We need some level of accuracy for nearby stops to be correct.
        gps.ready = (gps.position.coordinate.longitude &&
                     gps.position.coordinate.latitude &&
                     gps.position.horizontalAccuracy > 0 &&
                     gps.position.horizontalAccuracy < 1000) || false;

    }

}
