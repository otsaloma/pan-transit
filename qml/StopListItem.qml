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

ListItem {
    id: listItem
    contentHeight: nameLabel.height + descriptionLabel.height + repeater.height
    property var result: page.results[index]
    // Column width to be set based on data.
    property int lineWidth: 0
    Rectangle {
        id: bar
        anchors.bottom: repeater.bottom
        anchors.bottomMargin: 1.5 * Theme.paddingMedium
        anchors.left: parent.left
        anchors.leftMargin: Theme.horizontalPageMargin
        anchors.top: nameLabel.top
        anchors.topMargin: 1.5 * Theme.paddingMedium
        color: model.color
        radius: width / 3
        width: Theme.paddingSmall
    }
    Label {
        id: nameLabel
        anchors.left: bar.right
        anchors.leftMargin: Theme.paddingLarge
        anchors.right: parent.right
        anchors.rightMargin: Theme.horizontalPageMargin
        color: listItem.highlighted ? Theme.highlightColor : Theme.primaryColor
        height: implicitHeight + Theme.paddingLarge
        text: model.name
        truncationMode: TruncationMode.Fade
        verticalAlignment: Text.AlignBottom
    }
    Label {
        id: descriptionLabel
        anchors.left: bar.right
        anchors.leftMargin: Theme.paddingLarge
        anchors.right: parent.right
        anchors.rightMargin: Theme.horizontalPageMargin
        anchors.top: nameLabel.bottom
        color: Theme.secondaryColor
        font.pixelSize: Theme.fontSizeSmall
        height: implicitHeight + Theme.paddingSmall
        text: "%1 · %2".arg(model.description).arg(model.dist)
        truncationMode: TruncationMode.Fade
        verticalAlignment: Text.AlignVCenter
    }
    Repeater {
        // List at most three lines using the stop along with their destinations
        // to clarify which stop and on which side of the street it is located on.
        id: repeater
        anchors.left: descriptionLabel.left
        anchors.top: descriptionLabel.bottom
        height: Theme.paddingLarge
        model: listItem.result ? Math.min(3, listItem.result.lines.length) : 0
        width: parent.width
        Item {
            id: row
            anchors.left: repeater.left
            height: lineLabel.height
            width: listItem.width
            property var line: listItem.result.lines[index]
            Label {
                id: lineLabel
                anchors.left: row.left
                color: Theme.secondaryColor
                font.pixelSize: Theme.fontSizeSmall
                height: implicitHeight + Theme.paddingSmall
                horizontalAlignment: Text.AlignRight
                text: line.name
                verticalAlignment: Text.AlignVCenter
                width: listItem.lineWidth
                y: repeater.y + index * row.height
                Component.onCompleted: listItem.lineWidth =
                    Math.max(listItem.lineWidth, lineLabel.implicitWidth);
            }
            Label {
                id: destinationLabel
                anchors.left: lineLabel.right
                anchors.right: row.right
                anchors.rightMargin: Theme.horizontalPageMargin
                anchors.top: lineLabel.top
                color: Theme.secondaryColor
                font.pixelSize: Theme.fontSizeSmall
                height: implicitHeight + Theme.paddingSmall
                text: " → %1".arg(line.destination)
                truncationMode: TruncationMode.Fade
                verticalAlignment: Text.AlignVCenter
            }
            Component.onCompleted: repeater.height += row.height;
        }
    }
}
