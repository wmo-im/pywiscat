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

import json
import logging

from glob import glob
from io import BytesIO
from typing import Union
import zipfile

import click
from jsondiff import diff
from pywcmp.wcmp2.ets import WMOCoreMetadataProfileTestSuite2
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

    LOGGER.debug(f'Fetching GDC collection information from {gdc_url}')
    response = requests.get(gdc_url, params={'f': 'json'})
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


def prepare_record(data: dict) -> dict:
    """
    Prepare a record for parity checking

    :param record: `dict` of record

    :returns: `dict` of prepared record
    """

    keep_links = []

    LOGGER.debug('Pruning generated_by')
    _ = data.pop('generated_by', None)

    LOGGER.debug('Pruning wmo:topicHierarchy')
    _ = data['properties'].pop('wmo:topicHierarchy', None)

    LOGGER.debug('Pruning wmo:topicHierarchy')
    _ = data['properties'].pop('centre-id', None)

    LOGGER.debug('Pruning links')
    for link in data['links']:
        if link.get('rel', '') == 'license':
            keep_links.append(link)
        else:
            LOGGER.debug(f'Removing link {link}')

    data['links'] = keep_links

    return data


def compare(centre_id: str, archive_dir: str) -> Union[dict, None]:
    """
    Compare a GDC's content against all other GDCs

    :param centre_id: centre identifier
    :param archive_dir: archive directory

    :returns: `dict` of report/results
    """

    iut = None
    other_gdcs = {}
    report = {
        'invalid': [],
        'identical': [],
        'incorrect': []
    }

    for gdc in glob(f'{archive_dir}/*'):
        if centre_id in gdc:
            iut = gdc
        else:
            other_gdcs[gdc] = {}
            for wcmp2 in glob(f'{gdc}/*.json'):
                with open(wcmp2) as fh:
                    data = json.load(fh)
                    other_gdcs[gdc][data['id']] = data

    LOGGER.debug(f'IUT: {iut}')
    LOGGER.debug(f'Other GDCs: {list(other_gdcs.keys())}')

    if iut is None or not other_gdcs:
        msg = 'Nothing to compare!'
        LOGGER.warning(msg)
        return

    for wcmp2 in glob(f'{iut}/*.json'):
        LOGGER.info(f'Checking {wcmp2}')
        with open(wcmp2) as fh:
            data = prepare_record(json.load(fh))
            try:
                ts = WMOCoreMetadataProfileTestSuite2(data)
                ts.run_tests()
            except Exception as err:
                LOGGER.debug(f'ERROR on {wcmp2}: {err}')
                report['invalid'].append(data['id'])
                continue

            for key in other_gdcs.keys():
                if data['id'] not in other_gdcs[key]:
                    LOGGER.debug(f"ERROR: {data['id']} NOT in {key}")
                    report['incorrect'].append(data['id'])
                    continue

                data2 = prepare_record(other_gdcs[key][data['id']])

                LOGGER.info(f"Comparing {iut}/{data['id']} and {key}/{other_gdcs[key][data['id']]['id']}")  # noqa

                diff_ = diff(data, data2)
                if diff_:
                    msg = f"Variation between {iut}/{data['id']} and {key}/{other_gdcs[key][data['id']]['id']}"  # noqa
                    LOGGER.info(msg)
                    LOGGER.debug(diff_)
                    report['incorrect'].append(data['id'])
                else:
                    LOGGER.info('Records are identical')
                    report['identical'].append(data['id'])

    return report


@click.group()
def archive():
    """Run archive utilities against a WIS2 GDC"""

    pass


@click.command()
@click.pass_context
@cli_option_verbosity
@click.argument('output_dir')
@click.option('--global-discovery-catalogue',
              help=f'Global Discovery Catalogue (default={GDC_URL})',
              default=GDC_URL)
def get(ctx, global_discovery_catalogue, output_dir, verbosity='NOTSET'):
    """Download and extract archive"""

    gdc_url_ = global_discovery_catalogue

    click.echo(f'Downloading and extracting zipfile from {gdc_url_} to {output_dir}')  # noqa
    if not download_and_extract_archive(gdc_url_, output_dir):
        click.echo('Download and extract failed.  Set -v DEBUG for more information')  # noqa

    click.echo('Done')


@click.command('compare')
@click.pass_context
@cli_option_verbosity
@click.argument('archive_dir')
@click.option('--centre-id', help='GDC centre identifier')
def compare_(ctx, centre_id, archive_dir, verbosity='NOTSET'):
    """Compare GDC metadata archives"""

    if centre_id is None:
        raise click.ClickException('No centre-id specified')

    click.echo(f'Comparing {centre_id} GDC archive to all other GDCs in {archive_dir}')  # noqa
    report = compare(centre_id, archive_dir)

    invalid = len(report['invalid'])
    identical = len(report['identical'])
    incorrect = len(report['incorrect'])

    click.echo('\nResults')
    click.echo('=======\n')
    click.echo(f'Invalid: {invalid}')
    click.echo(f'Identical: {identical}')
    click.echo(f'Incorrect: {incorrect}')

    click.echo('\nDone')


archive.add_command(get)
archive.add_command(compare_)
