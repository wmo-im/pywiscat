pywiscat

[![Build Status](https://github.com/wmo-im/pywiscat/workflows/build%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/wmo-im/pywiscat/actions)

Pythonic API to WMO WIS Catalogue

pywiscat provides a Pythonic API atop of the WMO WIS Catalogue in support
of reporting and analysis of WIS Catalogue metadata.

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
