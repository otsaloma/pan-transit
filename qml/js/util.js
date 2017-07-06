/* -*- coding: utf-8-unix -*-
 *
 * Copyright (C) 2017 Osmo Salomaa
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

function addProperties(items, name, value) {
    // Assign name to value in-place in all given items.
    for (var i = 0; i < items.length; i++)
        items[i][name] = value;
}

function appendAll(model, items) {
    // Append all items to model.
    for (var i = 0; i < items.length; i++)
        model.append(items[i]);
}

function findMatches(query, candidates, max) {
    // Return an array of matches from among candidates.
    query = query.toLowerCase();
    var found = [];
    for (var i = 0; i < candidates.length; i++) {
        // Match at the start of candidate strings.
        var candidate = candidates[i].toLowerCase();
        if (query && candidate.indexOf(query) === 0)
            found.push(candidates[i]);
    }
    for (var i = 0; i < candidates.length; i++) {
        // Match later in the candidate strings.
        var candidate = candidates[i].toLowerCase();
        if (query.length === 0 || candidate.indexOf(query) > 0)
            found.push(candidates[i]);
    }
    found = found.slice(0, max);
    for (var i = 0; i < found.length; i++) {
        // Highlight matching portion in markup field.
        found[i] = {"text": found[i]};
        found[i].markup = Theme.highlightText(
            found[i].text, query, Theme.highlightColor);
    }
    return found;
}

function injectMatches(model, found, text, markup) {
    // Set array of matches into existing ListView model items.
    found = found.slice(0, model.count);
    for (var i = 0; i < found.length; i++) {
        model.setProperty(i, text, found[i].text);
        model.setProperty(i, markup, found[i].markup);
        model.setProperty(i, "visible", true);
    }
    for (var i = found.length; i < model.count; i++)
        model.setProperty(i, "visible", false);
}
