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
import Sailfish.Silica 1.0
import "."

import "js/util.js" as Util

Page {
    id: page
    allowedOrientations: app.defaultAllowedOrientations

    property string populatedProvider: ""

    SilicaGridView {
        id: view
        anchors.fill: parent
        cellHeight: Theme.itemSizeMedium
        cellWidth: {
            // Use a dynamic column count based on available screen width.
            var width = page.isPortrait ? Screen.width : Screen.height;
            return width / Math.floor(width / (Theme.pixelRatio * 400));
        }

        delegate: FavoriteListItem {
            id: listItem
            contentHeight: view.cellHeight
            enabled: !view.menuOpen
            width: view.cellWidth
            menu: ContextMenu {
                id: contextMenu
                MenuItem {
                    text: app.tr("Edit")
                    onClicked: page.editFavorite(model.index);
                }
                MenuItem {
                    text: app.tr("Remove")
                    onClicked: page.removeFavorite(listItem, model.index);
                }
                onActiveChanged: view.menuOpen = contextMenu.active;
            }
            ListView.onRemove: animateRemoval(listItem);
            onClicked: app.pageStack.push("FavoritePage.qml", {"props": model});
        }

        header: PageHeader {
            title: "Pan Transit"
        }

        model: ListModel {}

        property bool menuOpen: false

        PullDownMenu {

            MenuItem {
                text: app.tr("About")
                onClicked: app.pageStack.push("AboutPage.qml");
            }

            MenuItem {
                text: app.tr("Preferences")
                onClicked: app.pageStack.push("PreferencesPage.qml");
            }

            MenuItem {
                text: app.tr("Search")
                onClicked: {
                    app.pageStack.push("SearchPage.qml");
                    app.pageStack.pushAttached("SearchResultsPage.qml");
                }
            }

            MenuItem {
                enabled: gps.ready
                text: app.tr("Nearby")
                onClicked: app.pageStack.push("NearbyPage.qml");
            }

        }

        ViewPlaceholder {
            id: viewPlaceholder
            enabled: false
            hintText: app.tr("Pull down to select a provider and to search for stops.")
            text: app.tr("Once added, favorites appear here.")
        }

        BusyIndicator {
            anchors.left: parent.left
            anchors.leftMargin: Theme.horizontalPageMargin
            anchors.top: parent.top
            anchors.topMargin: Theme.horizontalPageMargin
            running: !gps.ready
            size: BusyIndicatorSize.Medium
        }

        VerticalScrollDecorator {}

    }

    Timer {
        id: timer
        interval: 5000
        repeat: true
        running: app.applicationActive && gps.ready && view.model.count > 0
        triggeredOnStart: true
        onTriggered: page.update();
    }

    Component.onCompleted: py.ready ? page.populate() :
        py.onReadyChanged.connect(page.populate);

    onStatusChanged: {
        if (page.status === PageStatus.Activating) {
            if (page.populatedProvider &&
                page.populatedProvider !== app.conf.get("provider"))
                page.populate();
            page.update();
        }
    }

    function editFavorite(index) {
        // Open separate page to edit favorite at index.
        var item = view.model.get(index);
        var dialog = pageStack.push("EditFavoritePage.qml", {
            "key": item.key, "name": item.name});
        dialog.accepted.connect(function() {
            py.call_sync("pan.app.favorites.rename", [item.key, dialog.name]);
            for (var i = 0; i < dialog.removals.length; i++)
                py.call_sync("pan.app.favorites.remove_stop", [item.key, dialog.removals[i]]);
            var color = py.call_sync("pan.app.favorites.get_color", [item.key]);
            view.model.setProperty(index, "name", dialog.name);
            view.model.setProperty(index, "color", color);
            py.call("pan.app.save", [], null);
        });
    }

    function populate() {
        // Load favorites from the Python backend.
        view.model.clear();
        var favorites = py.evaluate("pan.app.favorites.favorites");
        Util.addProperties(favorites, "near", false);
        Util.appendAll(view.model, favorites);
        viewPlaceholder.enabled = (view.model.count === 0);
        page.populatedProvider = app.conf.get("provider");
    }

    function removeFavorite(listItem, index) {
        // Remove favorite at index.
        listItem.remorseAction(app.tr("Removing"), function() {
            var item = view.model.get(index);
            py.call_sync("pan.app.favorites.remove", [item.key]);
            view.model.remove(index);
        });
    }

    function update() {
        // Update favorite display based on positioning.
        if (view.model.count === 0) return;
        var threshold = app.conf.get("favorite_highlight_radius");
        var favorites = py.evaluate("pan.app.favorites.favorites");
        for (var i = 0; i < view.model.count; i++) {
            var item = view.model.get(i);
            var dist = gps.position.coordinate.distanceTo(
                QtPositioning.coordinate(item.y, item.x));
            item.near = threshold < 1000000 ? (dist < threshold) : true;
            if (i >= favorites.length) continue;
            if (favorites[i].key !== item.key) continue;
            item.name = favorites[i].name;
            item.color = favorites[i].color;
            item.line_summary = favorites[i].line_summary;
        }
    }

}
