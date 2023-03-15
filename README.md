# pywiscat

[![Build Status](https://github.com/wmo-im/pywiscat/workflows/build%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/wmo-im/pywiscat/actions)

## Pythonic API to WMO WIS Catalogue

pywiscat provides a Pythonic API atop the WMO WIS Catalogue in support
of reporting and analysis of the WIS Catalogue and Metadata.

## Installation

### pip

Install latest stable version from [PyPI](https://pypi.org/project/pywiscat).

```bash
pip3 install pywiscat
```

### From source

Install latest development version.

```bash
python3 -m venv pywiscat
cd pywiscat
. bin/activate
git clone https://github.com/wmo-im/pywiscat.git
cd pywiscat
pip3 install -r requirements.txt
python3 setup.py build
python3 setup.py install
```

## Running

The canonical URL for the GDC is 'https://api.weather.gc.ca/collections/wis2-discovery-metadata.

To use a different catalogue, set the `PYWISCAT_GDC_URL` environmnent variable before running pywiscat.

From command line:

```bash
# fetch version
pywiscat --version

## WIS 1.0 workflows

# catalogue management

# download bundle of WIS metadata to disk
pywiscat wis1 catalogue cache --directory /path/to/metadata/files

# search for terms (case-insensitive) and group by organization

# search for 'nwp'
pywiscat wis1 report terms-by-org --directory=/path/to/metadata/files --term nwp

# search for 'nwp' and 'model' (exclusive)
pywiscat wis1 report terms-by-org --directory=/path/to/metadata/files --term nwp --term model

# search for 'nwp' in verbose mode (Python logging levels)
pywiscat wis1 report terms-by-org --directory=/path/to/metadata/files --term nwp --verbosity DEBUG

# KPI assesment

# run KPI assesment (aka pywcmp) on all metadata files in a directory with default ("brief") output
pywiscat wis1 report kpi --directory /path/to/metadata/files

# run KPI assesment on selected metadata files printing out the "summary" section for each file
pywiscat wis1 report kpi --file-list /path/to/metadata/file_list.json --output-format summary

# run assesment of KPI 1 (ATS) on all metadata files in a directory with "full" output
pywiscat wis1 report kpi -k1 --directory /path/to/metadata/files --output-format full

# other reports

# list number of records per organization
pywiscat wis1 report records-by-org --directory=/path/to/metadata/files

## WIS2 workflows

# search the WIS2 Global Discovery Catalogue (GDC)
pywiscat wis2 search

# search the WIS2 Global Discovery Catalogue (GDC) with a full text query
pywiscat wis2 search -q radar

# search the WIS2 Global Discovery Catalogue (GDC) with a bounding box query
pywiscat wis2 search --bbox -142,42.-52,84

# get more information about a WIS2 GDC record
pywiscat wis2 get urn:x-wmo:md:can:eccc-msc:c7c9d726-c48a-49e3-98ab-78a1ab87cda8
```

## Using the API
```python

## WIS 1.0 workflows

from pywiscat.wis1.catalogue import cache_catalogue
from pywiscat.wis1.report import group_search_results_by_organization

# catalogue management
status = cache_catalogue('/path/to/directory')

# search for terms (case-insensitive) and group by organization
results_dict = group_search_results_by_organization('path/to/directory', terms=['nwp', 'model'])

## WIS2 workflows

from pywiscat.wis2.catalogue import search, get

# search catalogue
results = search(q='radar', bbox=[-142, 42, -52, 84]))

# get a single catalogue record
results = get('urn:x-wmo:md:can:eccc-msc:c7c9d726-c48a-49e3-98ab-78a1ab87cda8')
```


## Development

```bash
python3 -m venv pywiscat
cd pywiscat
source bin/activate
git clone https://github.com/wmo-im/pywiscat.git
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
python3 setup.py install
```

### Running tests

```bash
# via setuptools
python3 setup.py test
# manually
python3 tests/run_tests.py
```

## Releasing

```bash
python3 setup.py sdist bdist_wheel --universal
twine upload dist/*
```

## Code Conventions

[PEP8](https://www.python.org/dev/peps/pep-0008)

## Issues

Issues are managed at https://github.com/wmo-im/pywiscat/issues

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
* [Ján Osuský](https://github.com/josusky)
