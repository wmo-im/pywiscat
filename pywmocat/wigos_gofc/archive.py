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

import click

from pywmocat.cli_helpers import cli_option_verbosity
from pywmocat.env import WIGOS_GOFC_URL
from pywmocat.uril import download_and_extract_archive

LOGGER = logging.getLogger(__name__)


@click.group()
def archive():
    """Run archive utilities against a WIGOS GOFC"""

    pass


@click.command()
@click.pass_context
@cli_option_verbosity
@click.argument('output_dir')
@click.option('--global-discovery-catalogue',
              help=f'Global Discovery Catalogue (default={WIGOS_GOFC_URL})',
              default=WIGOS_GOFC_URL)
def get(ctx, global_discovery_catalogue, output_dir, verbosity='NOTSET'):
    """Download and extract archive"""

    gofc_url_ = global_discovery_catalogue

    click.echo(f'Downloading and extracting zipfile from {gofc_url_} to {output_dir}')  # noqa
    if not download_and_extract_archive(gofc_url_, output_dir):
        click.echo('Download and extract failed.  Set -v DEBUG for more information')  # noqa

    click.echo('Done')


archive.add_command(get)
