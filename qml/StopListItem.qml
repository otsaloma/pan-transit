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
    contentHeight: nameLabel.height + descriptionLabel.height + linesLabel.height
    property var result: page.results[index]
    Rectangle {
        id: bar
        anchors.bottom: linesLabel.bottom
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
    Label {
        id: linesLabel
        anchors.left: bar.right
        anchors.leftMargin: Theme.paddingLarge
        anchors.right: parent.right
        anchors.rightMargin: Theme.horizontalPageMargin
        anchors.top: descriptionLabel.bottom
        color: Theme.secondaryColor
        font.pixelSize: Theme.fontSizeSmall
        height: text ? implicitHeight + Theme.paddingLarge : Theme.paddingLarge
        lineHeight: 1.1
        text: model.line_summary || ""
        truncationMode: TruncationMode.Fade
        verticalAlignment: Text.AlignTop
        wrapMode: model.line_summary.match(/\n/) ? Text.NoWrap : Text.WordWrap
    }
}
