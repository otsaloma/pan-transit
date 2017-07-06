/* -*- coding: utf-8-unix -*-
 *
 * Copyright (C) 2016 Osmo Salomaa
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

Page {
    id: page
    allowedOrientations: app.defaultAllowedOrientations

    SilicaFlickable {
        anchors.fill: parent
        contentHeight: column.height
        contentWidth: parent.width

        Column {
            id: column
            anchors.fill: parent

            PageHeader {
                title: app.tr("Preferences")
            }

            ValueButton {
                id: providerButton
                label: app.tr("Provider")
                height: Theme.itemSizeSmall
                value: py.evaluate("pan.app.provider.name")
                width: parent.width
                onClicked: {
                    var dialog = app.pageStack.push("ProviderPage.qml");
                    dialog.accepted.connect(function() {
                        providerButton.value = py.evaluate("pan.app.provider.name");
                    });
                }
            }

            SectionHeader {
                text: app.tr("Display")
            }

            TextField {
                id: radiusField
                inputMethodHints: Qt.ImhDigitsOnly | Qt.ImhNoPredictiveText
                label: app.tr("Favorite highlight radius (m)")
                text: app.conf.get("favorite_highlight_radius").toString()
                validator: RegExpValidator { regExp: /^[0-9]+$/ }
                width: parent.width
                EnterKey.enabled: text.length > 0
                EnterKey.iconSource: "image://theme/icon-m-enter-close"
                EnterKey.onClicked: radiusField.focus = false;
                Component.onCompleted: {
                    page.onStatusChanged.connect(function() {
                        if (!radiusField.text.match(/^[0-9]+$/)) return;
                        var value = parseInt(radiusField.text, 10);
                        app.conf.set("favorite_highlight_radius", value);
                    });
                }
            }

            TextField {
                id: cutOffField
                inputMethodHints: Qt.ImhDigitsOnly | Qt.ImhNoPredictiveText
                label: app.tr("Departure time cutoff (min)")
                text: app.conf.get("departure_time_cutoff").toString()
                validator: RegExpValidator { regExp: /^[0-9]+$/ }
                width: parent.width
                EnterKey.enabled: text.length > 0
                EnterKey.iconSource: "image://theme/icon-m-enter-close"
                EnterKey.onClicked: cutOffField.focus = false;
                Component.onCompleted: {
                    page.onStatusChanged.connect(function() {
                        if (!cutOffField.text.match(/^[0-9]+$/)) return;
                        var value = parseInt(cutOffField.text, 10);
                        app.conf.set("departure_time_cutoff", value);
                    });
                }
            }

            ListItemLabel {
                color: Theme.secondaryColor
                font.pixelSize: Theme.fontSizeSmall
                height: implicitHeight + 2 * Theme.paddingMedium
                text: app.tr("When the time remaining to departure is below cutoff, it is shown as minutes remaining instead of the departure time.")
                verticalAlignment: Text.AlignVCenter
                wrapMode: Text.WordWrap
            }

            ComboBox {
                id: unitsComboBox
                label: app.tr("Units")
                menu: ContextMenu {
                    MenuItem { text: app.tr("Metric") }
                    MenuItem { text: app.tr("American") }
                    MenuItem { text: app.tr("British") }
                }
                property var values: ["metric", "american", "british"]
                Component.onCompleted: {
                    var value = app.conf.get("units");
                    var index = unitsComboBox.values.indexOf(value);
                    unitsComboBox.currentIndex = index;
                }
                onCurrentIndexChanged: {
                    var index = unitsComboBox.currentIndex;
                    var value = unitsComboBox.values[index];
                    app.conf.set("units", value);
                }
            }
        }

        VerticalScrollDecorator {}

    }
}
