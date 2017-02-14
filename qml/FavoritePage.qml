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

Page {
    id: page
    allowedOrientations: app.defaultAllowedOrientations
    property bool canCover: true
    property var downloadTime: -1
    property var ignores: []
    property bool loading: false
    property bool populated: false
    property var props: {}
    property var results: {}
    property var stops: []
    property string title: ""
    // Column widths to be set based on data.
    property int lineWidth: 0
    property int realWidth: 0
    property int timeWidth: 0
    SilicaListView {
        id: view
        anchors.fill: parent
        delegate: Component {
            Loader {
                // Allow provider-specific layouts for departure list items.
                source: py.evaluate("pan.app.provider.departure_list_item_qml")
                width: view.width
            }
        }
        header: PageHeader { title: page.title }
        model: ListModel {}
        PullDownMenu {
            visible: !page.loading || false
            MenuItem {
                text: qsTranslate("", "Filter lines")
                onClicked: {
                    var options = {"stops": page.stops, "ignores": page.ignores};
                    var dialog = pageStack.push("LineFilterPage.qml", options);
                    dialog.accepted.connect(function() {
                        var args = [page.props.key, dialog.ignores];
                        py.call_sync("pan.app.favorites.set_ignore_lines", args);
                        view.model.clear();
                        page.loading = true;
                        page.title = "";
                        busy.text = qsTranslate("", "Loading");
                        page.populate();
                    });
                }
            }
        }
        VerticalScrollDecorator {}
    }
    BusyModal {
        id: busy
        running: page.loading
    }
    Timer {
        interval: 15000
        repeat: true
        running: app.running && page.populated
        triggeredOnStart: true
        onTriggered: page.update();
    }
    onStatusChanged: {
        if (page.populated) {
            return;
        } else if (page.status === PageStatus.Activating) {
            view.model.clear();
            page.loading = true;
            page.title = "";
            busy.text = qsTranslate("", "Loading");
        } else if (page.status === PageStatus.Active) {
            page.populate();
        }
    }
    function getModel() {
        // Return the list view model with current departures.
        return view.model;
    }
    function populate(silent) {
        // Load departures from the Python backend.
        silent = silent || false;
        silent || view.model.clear();
        var key = page.props.key;
        page.ignores = py.call_sync("pan.app.favorites.get_ignore_lines", [page.props.key]);
        page.stops = py.call_sync("pan.app.favorites.get_stop_ids", [page.props.key]);
        py.call("pan.app.favorites.find_departures", [key], function(results) {
            if (results && results.error && results.message) {
                silent || (page.title = "");
                silent || (busy.error = results.message);
            } else if (results && results.length > 0) {
                view.model.clear();
                page.lineWidth = 0;
                page.realWidth = 0;
                page.timeWidth = 0;
                page.results = results;
                page.title = page.props.name;
                for (var i = 0; i < results.length; i++) {
                    results[i].color_qml = ""
                    results[i].time_qml = ""
                    view.model.append(results[i]);
                }
            } else {
                silent || (page.title = "");
                silent || (busy.error = qsTranslate("", "No departures found"));
            }
            page.downloadTime = Date.now();
            page.loading = false;
            page.populated = true;
            view.forceLayout();
            page.update();
        });
        app.cover.update();
    }
    function update() {
        if (Date.now() - page.downloadTime >
            py.evaluate("pan.app.provider.update_interval") * 1000) {
            // Load new departures from the API.
            page.populate(true);
        } else {
            page.updateTimes();
            page.updateWidths();
            app.cover.update();
        }
    }
    function updateTimes() {
        // Update colors and times remaining to departure.
        for (var i = view.model.count - 1; i > -1; i--) {
            var item = view.model.get(i);
            var dist = gps.position.coordinate.distanceTo(
                QtPositioning.coordinate(item.y, item.x));
            item.time_qml = py.call_sync("pan.util.format_departure_time", [item.time]);
            item.color_qml = item.color || py.call_sync(
                "pan.util.departure_time_to_color", [dist, item.time]);
            // Remove departures already passed.
            item.time_qml || view.model.remove(i);
        }
    }
    function updateWidths() {
        // Update column widths based on visible items.
        var lineWidth = 0;
        var realWidth = 0;
        var timeWidth = 0;
        for (var i = 0; i < view.model.count; i++) {
            var item = view.model.get(i);
            lineWidth = Math.max(lineWidth, item.lineWidth || 0);
            realWidth = Math.max(realWidth, item.realWidth || 0);
            timeWidth = Math.max(timeWidth, item.timeWidth || 0);
        }
        page.lineWidth = lineWidth;
        page.realWidth = realWidth;
        page.timeWidth = timeWidth;
    }
}
