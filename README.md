# pywiscat

[![Build Status](https://github.com/wmo-im/pywiscat/workflows/build%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/wmo-im/pywiscat/actions)

## Pythonic API to WMO WIS Catalogue

pywiscat provides a Pythonic API atop the WMO WIS2 Catalogue in support
of reporting and analysis of the WIS2 Catalogue and its associated discovery metadata.

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

The canonical URL for the GDC is https://api.weather.gc.ca.

To use a different catalogue, set the `PYWISCAT_GDC_URL` environmnent variable before running pywiscat.

From command line:

```bash
# fetch version
pywiscat --version

## WIS2 workflows

# search the WIS2 Global Discovery Catalogue (GDC)
pywiscat search

# search the WIS2 Global Discovery Catalogue (GDC) with a full text query
pywiscat search --query radar

# search the WIS2 Global Discovery Catalogue (GDC) for only recommended data
pywiscat search --data-policy recommended

# search the WIS2 Global Discovery Catalogue (GDC) with a bounding box query
pywiscat search --bbox -142,42,-52,84

# get more information about a WIS2 GDC record
pywiscat get urn:x-wmo:md:can:eccc-msc:c7c9d726-c48a-49e3-98ab-78a1ab87cda8
```

## Using the API
```python

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
# create release (x.y.z is the release version)
vi pywiscat/__init__.py  # update __version__
git commit -am 'update release version x.y.z'
git push origin master
git tag -a x.y.z -m 'tagging release version x.y.z'
git push --tags

# upload to PyPI
rm -fr build dist *.egg-info
python3 setup.py sdist bdist_wheel --universal
twine upload dist/*

# publish release on GitHub (https://github.com/wmo-im/pywiscat/releases/new)

# bump version back to dev
vi pywiscat/__init__.py  # update __version__
git commit -am 'back to dev'
git push origin master
```

## Code Conventions

[PEP8](https://www.python.org/dev/peps/pep-0008)

## Issues

Issues are managed at https://github.com/wmo-im/pywiscat/issues

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
* [Ján Osuský](https://github.com/josusky)
