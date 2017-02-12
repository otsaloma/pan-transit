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

ListItem {
    id: listItem
    contentHeight: Theme.itemSizeMedium
    enabled: false
    property var result: page.results[index]
    Rectangle {
        id: bar
        anchors.bottom: destinationLabel.bottom
        anchors.bottomMargin: Theme.paddingMedium
        anchors.left: parent.left
        anchors.leftMargin: Theme.horizontalPageMargin
        anchors.top: lineLabel.top
        anchors.topMargin: Theme.paddingMedium
        color: model.color_qml
        radius: width / 3
        width: Theme.paddingSmall
    }
    Label {
        id: lineLabel
        anchors.bottom: parent.verticalCenter
        anchors.left: bar.right
        anchors.leftMargin: Theme.paddingLarge
        anchors.right: realLabel.left
        anchors.top: parent.top
        text: model.line
        truncationMode: TruncationMode.Fade
        verticalAlignment: Text.AlignBottom
    }
    Label {
        id: dotLabel
        anchors.baseline: lineLabel.baseline
        color: Theme.secondaryColor
        truncationMode: TruncationMode.Fade
        width: Math.max(0, realLabel.x - x)
        x: lineLabel.x + lineLabel.implicitWidth + Theme.paddingSmall
        Component.onCompleted: {
            // Add a dotted line long enough for all orientations.
            var dots = " . . . . . . . . . . . . . . . . . . . .";
            var dots = dots + dots + dots + dots + dots;
            var size = Math.max(page.width, page.height);
            while (dotLabel.implicitWidth < size) {
                var prev = dotLabel.implicitWidth;
                dotLabel.text += dots;
                if (dotLabel.implicitWidth < prev + 1) break;
            }
        }
    }
    Label {
        id: destinationLabel
        anchors.left: bar.right
        anchors.leftMargin: Theme.paddingLarge
        anchors.right: parent.right
        anchors.rightMargin: Theme.horizontalPageMargin
        anchors.top: parent.verticalCenter
        anchors.bottom: parent.bottom
        color: Theme.secondaryColor
        font.pixelSize: Theme.fontSizeSmall
        text: model.destination
        truncationMode: TruncationMode.Fade
        verticalAlignment: Text.AlignTop
    }
    Label  {
        id: realLabel
        anchors.baseline: lineLabel.baseline
        anchors.right: timeLabel.left
        anchors.rightMargin: page.realWidth > 0 ? Theme.paddingLarge : 0
        color: Theme.secondaryColor
        font.pixelSize: Theme.fontSizeSmall
        horizontalAlignment: Text.AlignRight
        text: model.realtime ? "R" : ""
        width: page.realWidth
        Component.onCompleted: realLabel.updateWidth();
        onTextChanged: realLabel.updateWidth();
        function updateWidth() {
            var width = realLabel.implicitWidth;
            view.model.setProperty(model.index, "realWidth", width);
            page.realWidth = Math.max(page.realWidth, width);
        }
    }
    Label {
        id: timeLabel
        anchors.baseline: lineLabel.baseline
        anchors.right: parent.right
        anchors.rightMargin: Theme.horizontalPageMargin
        horizontalAlignment: Text.AlignRight
        text: model.time_qml
        width: page.timeWidth
        Component.onCompleted: timeLabel.updateWidth();
        onTextChanged: timeLabel.updateWidth();
        function updateWidth() {
            var width = timeLabel.implicitWidth;
            view.model.setProperty(model.index, "timeWidth", width);
            page.timeWidth = Math.max(page.timeWidth, width);
        }
    }
    ListView.onRemove: animateRemoval(listItem);
}
