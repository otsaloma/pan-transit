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

import "js/util.js" as Util

Page {
    id: page
    allowedOrientations: app.defaultAllowedOrientations
    canNavigateForward: app.searchQuery.length > 0

    property var history: []

    SilicaListView {
        id: view
        anchors.fill: parent
        // Prevent list items from stealing focus.
        currentIndex: -1

        delegate: ListItem {
            id: listItem
            contentHeight: visible ? Theme.itemSizeSmall : 0
            menu: contextMenu
            visible: model.visible

            ListItemLabel {
                anchors.leftMargin: view.searchField.textLeftMargin
                color: listItem.highlighted ? Theme.highlightColor : Theme.primaryColor
                height: Theme.itemSizeSmall
                text: model.text
            }

            ContextMenu {
                id: contextMenu
                MenuItem {
                    text: app.tr("Remove")
                    onClicked: {
                        py.call_sync("pan.app.history.remove", [model.name]);
                        var index = page.history.indexOf(model.name);
                        index > -1 && page.history.splice(index, 1);
                        view.model.setProperty(model.index, "visible", false);
                    }
                }
            }

            ListView.onRemove: animateRemoval(listItem)

            onClicked: {
                app.searchQuery = model.name;
                app.pageStack.navigateForward();
            }

        }

        header: Column {
            height: header.height + searchField.height
            width: parent.width

            PageHeader {
                id: header
                title: app.tr("Search")
            }

            SearchField {
                id: searchField
                placeholderText: app.tr("Search")
                width: parent.width
                EnterKey.enabled: text.length > 0
                EnterKey.onClicked: app.pageStack.navigateForward();
                onTextChanged: {
                    app.searchQuery = searchField.text;
                    page.filterHistory();
                }
            }

            Component.onCompleted: view.searchField = searchField;

        }

        model: ListModel {}

        property var searchField

        ViewPlaceholder {
            id: viewPlaceholder
            enabled: false
            hintText: app.tr("You can search for stops by name, number or address, depending on the provider.")
        }

        VerticalScrollDecorator {}

    }

    onStatusChanged: {
        if (page.status === PageStatus.Activating) {
            page.loadHistory();
            page.filterHistory();
        }
    }

    function filterHistory() {
        // Filter search history for the current search field text.
        var query = view.searchField.text;
        var found = Util.findMatches(query, page.history, view.model.count);
        Util.injectMatches(view.model, found, "name", "text");
        viewPlaceholder.enabled = found.length === 0;
    }

    function loadHistory() {
        // Load search history and preallocate list items.
        page.history = py.evaluate("pan.app.history.queries");
        while (view.model.count < 50)
            view.model.append({"name": "",
                               "text": "",
                               "visible": false});

    }

}
