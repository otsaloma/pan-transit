Pan Transit
===========

[![Build Status](https://travis-ci.org/otsaloma/pan-transit.svg)](
https://travis-ci.org/otsaloma/pan-transit)

Pan Transit is an application for Sailfish OS to view departures from
public transport stops. It is designed to support multiple different
providers (i.e. cities/regions). For current support, look under the
[`providers`](providers) directory.

Pan Transit is free software released under the GNU General Public
License (GPL), see the file [`COPYING`](COPYING) for details.

For testing purposes you can just run `qmlscene qml/pan-transit.qml`.
For installation, you can build the RPM package with command `make rpm`.
You don't need an SDK to build the RPM, only basic tools: `make`,
`rpmbuild`, `gettext` and `linguist` from `qttools`
