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

CoverBackground {
    id: cover
    anchors.fill: parent
    property bool active: status === Cover.Active
    Label {
        id: title
        anchors.centerIn: parent
        color: Theme.primaryColor
        font.family: Theme.fontFamilyHeading
        font.pixelSize: Theme.fontSizeLarge
        horizontalAlignment: Text.AlignHCenter
        text: "Pan\nTransit"
        width: parent.width
    }
    SilicaListView {
        id: view
        anchors.centerIn: parent
        width: parent.width
        delegate: Item {
            id: listItem
            height: lineLabel.height
            width: parent.width
            Label {
                id: lineLabel
                anchors.left: parent.left
                anchors.right: parent.horizontalCenter
                anchors.rightMargin: Theme.paddingLarge / 2
                font.pixelSize: Theme.fontSizeLarge
                height: implicitHeight + 2 * Theme.paddingSmall
                horizontalAlignment: Text.AlignRight
                text: model.line
                truncationMode: TruncationMode.Fade
                verticalAlignment: Text.AlignVCenter
            }
            Label {
                id: timeLabel
                anchors.baseline: lineLabel.baseline
                anchors.left: parent.horizontalCenter
                anchors.leftMargin: Theme.paddingLarge / 2
                anchors.right: parent.right
                font.pixelSize: Theme.fontSizeMedium
                height: implicitHeight + 2 * Theme.paddingSmall
                horizontalAlignment: Text.AlignLeft
                text: model.time
                truncationMode: TruncationMode.Fade
                verticalAlignment: Text.AlignVCenter
            }
            Component.onCompleted: view.height = view.model.count * listItem.height;
        }
        model: ListModel {}
    }
    Timer {
        // Update times remaining periodically.
        interval: 30000
        repeat: true
        running: app.running
        triggeredOnStart: true
        onTriggered: cover.update();
    }
    Component.onCompleted: {
        // Pre-fill list view model with blank entries.
        for (var i = 0; i < 5; i++)
            view.model.append({"line": "", "time": ""});
        app.pageStack.onCurrentPageChanged.connect(cover.update);
    }
    function clear() {
        // Clear the visible list of departures.
        for (var i = 0; i < view.model.count; i++) {
            view.model.setProperty(i, "line", "");
            view.model.setProperty(i, "time", "");
        }
    }
    function copyFrom(model) {
        // Copy departure items from given model.
        for (var i = 0, j = 0; i < model.count && j < view.model.count; i++) {
            if (!model.get(i).visible) continue;
            view.model.setProperty(j, "line", model.get(i).line);
            view.model.setProperty(j, "time", model.get(i).time_qml);
            j++;
        }
    }
    function update() {
        // Query departures from the current page.
        var page = app.pageStack.currentPage;
        var model = null;
        var countVisible = 0;
        if (page && page.canCover) {
            var model = page.getModel();
            for (var i = 0; i < model.count; i++) {
                // Departures can be hidden by line filters.
                if (model.get(i).visible)
                    countVisible++;
            }
            if (model && countVisible > 0) {
                // Show the first few departures.
                cover.clear();
                cover.copyFrom(model);
                title.visible = false;
            }
        }
        if (!model || countVisible === 0) {
            // No departures; show title.
            cover.clear();
            title.visible = true;
        }
    }
}
