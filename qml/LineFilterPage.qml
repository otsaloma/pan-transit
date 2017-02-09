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
import "."

Dialog {
    id: page
    allowedOrientations: app.defaultAllowedOrientations
    property var ignores: []
    property bool loading: false
    property var stops: []
    SilicaGridView {
        id: view
        anchors.fill: parent
        cellWidth: {
            // Use a dynamic column count based on available screen width.
            var width = page.isPortrait ? Screen.width : Screen.height;
            width = width - Theme.horizontalPageMargin;
            return width / Math.floor(width / (Theme.pixelRatio * 200));
        }
        // Prevent list items from stealing focus.
        currentIndex: -1
        delegate: ListItem {
            id: listItem
            clip: true
            contentHeight: lineSwitch.height
            width: view.cellWidth
            TextSwitch {
                id: lineSwitch
                checked: model.checked
                description: model.destination
                text: model.name
                // Avoid wrapping description.
                width: 3 * page.width
                Component.onCompleted: view.cellHeight = lineSwitch.height;
                onCheckedChanged: view.model.setProperty(
                    model.index, "checked", lineSwitch.checked);
            }
            OpacityRampEffect {
                direction: OpacityRamp.LeftToRight
                offset: (view.cellWidth - Theme.paddingLarge) / lineSwitch.width
                slope: lineSwitch.width / Theme.paddingLarge
                sourceItem: lineSwitch
            }
        }
        header: DialogHeader {}
        model: ListModel {}
        PullDownMenu {
            id: menu
            visible: !page.loading && view.model.count > 0
            MenuItem {
                text: qsTranslate("", "Mark all")
                onClicked: menu.setAllChecked(true);
            }
            MenuItem {
                text: qsTranslate("", "Unmark all")
                onClicked: menu.setAllChecked(false);
            }
            function setAllChecked(checked) {
                for (var i = 0; i < view.model.count; i++)
                    view.model.setProperty(i, "checked", checked);
            }
        }
        VerticalScrollDecorator {}
    }
    BusyModal {
        id: busy
        running: page.loading
    }
    Component.onCompleted: {
        page.loading = true;
        busy.text = qsTranslate("", "Loading")
        page.populate();
    }
    onAccepted: {
        // Construct an array out of unchecked lines.
        page.ignores = [];
        for (var i = 0; i < view.model.count; i++) {
            var item = view.model.get(i);
            item.checked || page.ignores.push({
                "name": item.name,
                "destination": item.destination
            });
        }
    }
    function populate() {
        // Load lines from the Python backend.
        view.model.clear();
        py.call("pan.app.provider.find_lines", [page.stops], function(results) {
            if (results && results.error && results.message) {
                busy.error = results.message;
            } else if (results && results.length > 0) {
                for (var i = 0; i < results.length; i++) {
                    results[i].checked = true;
                    for (var j = 0; j < page.ignores.length; j++)
                        if (page.ignores[j].name.toLowerCase() ===
                            results[i].name.toLowerCase() &&
                            page.ignores[j].destination.toLowerCase() ===
                            results[i].destination.toLowerCase())
                            results[i].checked = false;
                    view.model.append(results[i]);
                }
            } else {
                busy.error = qsTranslate("", "No lines found");
            }
            page.loading = false;
        });
    }
}
