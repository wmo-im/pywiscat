# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2026 Tom Kralidis
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

import logging

from io import BytesIO
import zipfile

import click
import requests

from pywiscat.cli_helpers import cli_option_verbosity
from pywiscat.env import GDC_URL

LOGGER = logging.getLogger(__name__)


def download_and_extract_archive(gdc_url: str, output_dir: str) -> bool:
    """
    Download and extract a metadata archive zipfile from a WIS2 GDC

    :param gdc_url: URL of WIS2 GDC
    :param output_dir: output directory

    :returns: `bool` of result
    """

    archive_link = None

    LOGGER.debug(f'Fetching GDC collection information from {GDC_URL}')
    response = requests.get(GDC_URL)
    response.raise_for_status()

    response = response.json()

    for link in response['links']:
        if link.get('rel') == 'archives':
            archive_link = link['href']
            LOGGER.debug(f'Archive link found: {archive_link}')
            break

    if archive_link is None:
        LOGGER.warning('Archive link not found')
        return False

    LOGGER.debug(f'Fetching metadata archive zipfile from {archive_link}')
    response = requests.get(archive_link)
    response.raise_for_status()

    LOGGER.debug(f'Extracting zipfile to {output_dir}')
    with zipfile.ZipFile(BytesIO(response.content)) as fh:
        fh.extractall(output_dir)

    return True


@click.group()
def archive():
    """Run archive utilities against a WIS2 GDC"""

    pass


@click.command()
@click.pass_context
@cli_option_verbosity
@click.argument('output_dir')
def get(ctx, output_dir, verbosity='NOTSET'):
    """Download and extract archive"""

    click.echo(f'Downloading and extracting zipfile from {GDC_URL} to {output_dir}')  # noqa
    if not download_and_extract_archive(GDC_URL, output_dir):
        click.echo('Download and extract failed.  Set -v DEBUG for more information')  # noqa

    click.echo('Done')


archive.add_command(get)
