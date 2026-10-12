# pywmocat

[![Build Status](https://github.com/wmo-im/pywmocat/workflows/build%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/wmo-im/pywmocat/actions)

## Pythonic API to WIS2 Global Discovery Catalogue / WIGOS Global Observing Facility Catalogue

pywmocat provides a Pythonic API atop the WIS2 Global Discovery Catalogue (GDC) and the WIGOS Global Observing Catalogue (GOFC).

## Installation

### pip

Install latest stable version from [PyPI](https://pypi.org/project/pywmocat).

```bash
pip3 install pywmocat
```

### From source

Install latest development version.

```bash
python3 -m venv pywmocat
cd pywmocat
. bin/activate
git clone https://github.com/wmo-im/pywmocat.git
cd pywmocat
pip3 install .
```

## Running

### WIS2 GDC workflows

The default WIS2 GDC used in pywmocat is https://wis2-gdc.weather.gc.ca/collections/wis2-discovery-metadata.

To use a different WIS2 GDC, set the `PYWMOCAT_WIS2_GDC_URL` environment variable before running pywmocat.

TODO: add default GOFC endpoint.

To use a different WIGOS GOFC, set the `PYWMOCAT_WIGOS_GOFC_URL` environment variable before running pywmocat.

From command line:

```bash
# fetch version
pywmocat --version

# search the WIS2 Global Discovery Catalogue (GDC)
pywmocat wis2-gdc search

# search the WIS2 Global Discovery Catalogue (GDC) with a full text query
pywmocat wis2-gdc search --query radar

# search the WIS2 Global Discovery Catalogue (GDC) for only recommended data
pywmocat wis2-gdc search --data-policy recommended

# search the WIS2 Global Discovery Catalogue (GDC) by country
pywmocat wis2-gdc search --country Germany

# search the WIS2 Global Discovery Catalogue (GDC) with a bounding box query
pywmocat wis2-gdc search --bbox -142,42,-52,84

# get more information about a WIS2 GDC record
pywmocat wis2-gdc get urn:wmo:md:ca-eccc-msc:6d483864-0ec9-4cd6-8cf8-453e14fc9213

### Archive utilities

# download and extract a WIS2 GDC metadata archive zipfile to a specific directory
# downloads from PYWMOCAT_WIS2_GDC_URL by default
# override with --global-discovery-catalogue (https://example.org/collections/wis2-discovery-metadata)
pywmocat wis2-gdc archive get /path/to/archive

# compare GDC metadata archive zipfile to other GDC metadata archive zipfiles
# this requires each GDC metadata archive zipfile to be downloaded and extracted via
# pywmocat archive get /path/to/archive (directory MUST be identical)
pywmocat wis2-gdc archive compare /path/archive --centre-id ca-eccc-msc-global-discovery-catalogue

### Metrics analyzers

# analyze core records by centre identifier
pywmocat wis2-gdc metrics core /path/to/archive

# analyze recommended records by centre identifier
pywmocat wis2-gdc metrics recommended /path/to/archive

# analyze Earth system disciplines by centre identifier
pywmocat wis2-gdc metrics earth-system-discipline /path/to/archive

# analyze Key Performance Indicators (KPIs) by centre identifier
pywmocat wis2-gdc metrics kpi ca-eccc-msc /path/to/archive
```

### Using the API
```python

from pywmocat.wis2_gdc.catalogue import search, get

# search catalogue
results = search(q='radar', bbox=[-142, 42, -52, 84]))

# get a single catalogue record
results = get('urn:x-wmo:md:can:eccc-msc:c7c9d726-c48a-49e3-98ab-78a1ab87cda8')
```

### WIGOS GOFC workflows

# search the WIGOS Global Observing Catalogue (GOFC)
pywmocat wigos-gofc search

# search the WIGOS Global Observing Catalogue (GOFC) with a full text query
pywmocat wigos-gofc search --query temperature

# search the WIGOS Global Observing Catalogue (GOFC) with a bounding box query
pywmocat wigos-gofc search --bbox -142,42,-52,84

# get more information about a WMDR record
pywmocat wigos-gofc get 0-20000-0-87344

### Archive utilities

# download and extract a WIGOS GOFC metadata archive zipfile to a specific directory
# downloads from PYWMOCAT_WIGOS_GOFC_URL by default
# override with --global-discovery-catalogue (https://example.org/collections/wigos-observing-facility-metadata)
pywmocat wigos-gofc archive get /path/to/archive


### Using the API
```python

from pywmocat.wigos_gofc.catalogue import search, get

# search catalogue
results = search(q='temperature', bbox=[-142, 42, -52, 84]))

# get a single catalogue record
results = get('0-20000-0-87344')
```

## Development

```bash
python3 -m venv pywmocat
cd pywmocat
source bin/activate
git clone https://github.com/wmo-im/pywmocat.git
pip3 install .
```

### Running tests

```bash
python3 tests/run_tests.py
```

## Releasing

```bash
# create release (x.y.z is the release version)
vi pyproject.toml  # update [project]/version
git commit -am 'update release version x.y.z'
git push origin master
git tag -a x.y.z -m 'tagging release version x.y.z'
git push --tags

# upload to PyPI
rm -fr build dist *.egg-info
python3 -m build
twine upload dist/*

# publish release on GitHub (https://github.com/wmo-im/pywmocat/releases/new)

# bump version back to dev
vi pyproject.toml  # update [project]/version
git commit -am 'back to dev'
git push origin master
```

## Code Conventions

[PEP8](https://www.python.org/dev/peps/pep-0008)

## Issues

Issues are managed at https://github.com/wmo-im/pywmocat/issues

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
* [Ján Osuský](https://github.com/josusky)
