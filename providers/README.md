Implementing a Transit Provider
===============================

To implement a transit data provider, you need to write two files: a
JSON metadata file and a Python file that implements four functions that
return transit data that your code fetches from your provider's API and
transforms into the format understood by Pan Transit. The functions you
need to write are documented below.

To download data you should always use `pan.http.get`,
`pan.http.get_json` etc. in order to use Pan Transit's user-agent and
default timeout and error handling. See the providers shipped with Pan
Transit for examples.

Use `~/.local/share/harbour-pan-transit/providers` as a local installation
directory in which to place your files. Restart Pan Transit, and your provider
should be loaded, listed and available for use. During development,
consider keeping your files under the Pan Transit source tree and using
the Python interpreter or a test script, e.g.

```python
>>> import pan
>>> provider = pan.Provider("digitransit_hsl")
>>> provider.find_stops("lasipalatsi", 24, 60)
```

and qmlscene (`qmlscene qml/pan-maps.qml`) for testing. Once your
provider is ready for wider use, send a pull request on
[GitHub][pull-request] to have it added to the repository and shipped as
part of Pan Transit.

[pull-request]: https://github.com/otsaloma/pan-transit/pulls

## JSON metadata file

```json
{
    "_name": "Helsinki",
    "_description": "Helsinki Region Transport (HSL)",
    "departure_list_item_qml": "DepartureListItemHsl.qml",
    "update_interval": 60
}
```

* **`name`** and **`description`** are visible to the user in the
  provider selection screen. Use underscore prefixes if the values of
  the fields are translatable. If your provider requires some copyright
  statement or attribution, you can include that in the description.

* **`departure_list_item_qml`** should be the name of the QML file used
  for list items of individual departures. Currently there's two
  choices: `DepartureListItemHsl.qml`, a compact display suitable for
  short line names, and `DepartureListItemTfl.qml`, a two-line display
  suitable for longer line names.

* **`update_interval`** should be the time in seconds between which new
  API calls are made to request departures. If your API provides
  real-time data or considerably limits the amount of departures
  returned per call, you might want to set this low, e.g. 60–300
  seconds, otherwise something higher to avoid unnecessary data traffic.

## Python code

### `find_departures(stops)`

`find_departures` returns a list of departures and their metadata for a
list of stops. The argument `stops` is a list of stop IDs. The return
value should be something like

```python
[
    {
        "destination": "Munkkiniemi",
        "line": "4",
        "realtime": False,
        "scheduled_time": 1486957140,
        "stop": "HSL:1020444",
        "time": 1486957140,
    }, ...
]
```

where

* **`color` (optional)** can be used to provide departure-specific
  colors, e.g. official colors for individual metro lines. If omitted,
  departures will be colored based on comparing the stop coordinates and
  the users position and calculating which departures the user cannot
  reach in time (red), which need fast walking or running (yellow) and
  which require no hurry (blue).

* **`destination`** should be the name of the final destination of the
  line or the headsign of the vehicle or something similar.

* **`line`** should be the name (string) of the line. Usually this is a
  number or a letter or some combination of them. If your lines don't
  have short names, you can use the vehicle type here, e.g. "Bus", which
  together with destination should identify the line.

* **`realtime`** should be `True` for departure times which are
  real-time, i.e. based on GPS-positioning etc. and take into account
  vehicles being late or early, or `False` if times are schedule data.

* **`scheduled_time`** should be the scheduled Unix time of departure.
  This is not currently used, but could be used in the future to
  indicate how many minutes late a departure is by comparing it with the
  real-time departure time.

* **`stop`** should be the stop ID copied from the function argument
  into the return value. When multiple stops are given as arguments,
  this is used connect departures later with stop metadata.

* **`time`** should be the Unix time of departure. This is what is shown
  to the user. If real-time data is available, it should be used here,
  otherwise it should be schedule data.

* **`x`** and **`y` (both optional)** should be the WGS 84 longitude and
  latitude coordinates of the stop from which the departure leaves.
  Provide these only if your API directly returns them. If these are
  left out, Pan Transit will fill them in based on coordinates saved
  along with a favorite, or seen earlier as part of a `find_stops` or
  `find_nearby_stops` call.

### `find_lines(stops)`

`find_lines` returns a list of lines and their metadata for a list of
stops. The argument `stops` is a list of stop IDs. The return value
should be something like

```python
[
    {
        "color": "#00985f",
        "destination": "Munkkiniemi",
        "id": "HSL:1004",
        "name": "4",
    }, ...
]
```

* **`color`** color should be whatever color your local transit agency
  uses for a particular line or a vehicle type. This is currently not
  shown for individual lines, but for stops, i.e. if bus and tram lines
  are assigned different colors, then bus and tram stops will be colored
  differently.

* **`destination`** should be the name of the final destination of the
  line or the headsign of the vehicle or something similar.

* **`id`** should be the unique ID (string) of the line. If your API
  does not provide line IDs, but the line names are unique, then
  duplicate the names as IDs.

* **`name`** should be the name (string) of the line. Usually this is a
  number or a letter or some combination of them. If your lines don't
  have short names, you can use the vehicle type here, e.g. "Bus", which
  together with destination should identify the line.

### `find_nearby_stops(x, y)`

`find_nearby_stops` returns a list of stops and their metadata around
the the given WGS 84 coordinates. The return value should be something
like

```python
[
    {
        "color": "#007ac9",
        "description": "Albertinkatu 10",
        "id": "HSL:1050110",
        "line_summary": "14 → Hernesaari\n17 → Viiskulma\n18 → Eira",
        "name": "Merimiehenkatu (1172)",
        "x": 24.937910200000015,
        "y": 60.160916900000124,
    }, ...
]
```

* **`color`** should be the color used to display the stop in listings
  among other stops. You can use whatever color your local transit
  agency uses to refer to a particular line or a vehicle type.

* **`description`** should be a short one-line description of the stop,
  e.g. an address. If your API does not provide this, you can e.g. list
  the vehicle types ("Bus, tram") or use something as generic as "Stop".

* **`id`** should be the unique ID (string) of the stop. If your API
  does not provide stop IDs, but the stop names are unique, then
  duplicate the names as IDs.

* **`line_summary`** should be a single or multiple line string summary
  of the lines passing through the stop. These are used in stop listings
  to provide additional details. If your provider groups different
  directions as a single stop, you might want just a line listing, e.g.
  "14, 17, 18". If different directions have separate stops, you might
  want to include destinations as in the above example.

* **`name`** should be the name of the stop and is shown prominently as
  first thing in stop listings and page title when viewing departures.

* **`x`** and **`y`** should be the WGS 84 longitude and latitude
  coordinates of the stop.

### `find_stops(query, x, y)`

`find_stops` returns a list if stops and their metadata based on a given
query. The query is a string, which depending on your API, you can use
to match against stop names, IDs, addresses, etc. The return value is
identical as above in `find_nearby_stops`.
