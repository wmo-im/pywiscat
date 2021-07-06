# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#          Ján Osuský <jan.osusky@iblsoft.com>
#
# Copyright (c) 2021 Tom Kralidis
# Copyright (c) 2021 IBL Software Engineering spol. s r. o.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import io
import json
import logging
import os
from urllib.request import urlopen
import tarfile

import click

from pywiscat.cli_helpers import cli_callbacks, cli_option_directory
from pywiscat.wis1.util import search_files_by_term

LOGGER = logging.getLogger(__name__)


def cache_catalogue(directory: str) -> bool:
    """
    Cache local copy of WIS catalogue

    :param directory: target directory path

    :returns: bool of cache result/status
    """

    zipfile_url = 'https://gisc.dwd.de/oaidownload/wis-catalogue.tar.gz'
    LOGGER.debug(f'Downloading WIS 1.0 Catalogue from {zipfile_url}')

    os.makedirs(directory, exist_ok=True)
    content = io.BytesIO(urlopen(zipfile_url).read())
    with tarfile.open(fileobj=content, mode='r:gz') as z:
        z.extractall(directory)

    return True


@click.group()
def catalogue():
    """Catalogue functions"""
    pass


@click.command()
@click.pass_context
@cli_callbacks
@cli_option_directory
def cache(ctx, directory, verbosity):
    """Cache a local copy of catalogue"""

    click.echo('Caching WIS 1.0 Catalogue')
    _ = cache_catalogue(directory)

    click.echo('Done')


catalogue.add_command(cache)


@click.command()
@click.pass_context
@cli_callbacks
@cli_option_directory
@click.option('--term', '-t', 'terms', multiple=True, required=True,
              help='Terms (sub-strings) to be searched in the metadata, case insensitive')
def search(ctx, terms, directory, verbosity):
    """Searches terms in the catalog (local directory with MD XML)"""

    results = search_files_by_term(directory, terms)

    if results:
        click.echo(json.dumps(results, indent=4))
    else:
        click.echo('No results')


catalogue.add_command(search)
