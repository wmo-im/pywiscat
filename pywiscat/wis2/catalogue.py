# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2023 Tom Kralidis
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
import os
from textwrap import indent, wrap

import click
import flag
from iso3166 import countries
from prettytable import PrettyTable
import requests

from pywiscat.cli_helpers import cli_option_verbosity
LOGGER = logging.getLogger(__name__)

GDC_URL = os.environ.get(
    'PYWISCAT_GDC_URL', 'https://api.weather.gc.ca/collections/wis2-discovery-metadata')  # noqa


def get_country_and_centre(identifier):
    """
    Get country and centre id from a WCMP2 identifier

    :param identifier: record identifier

    :returns: `tuple` of country and centre id
    """

    tokens = identifier.split(':')

    return tokens[3], tokens[4]


def get_country_prettified(country):
    """
    Get expanded country description

    :param country: ISO 3166-3 country name

    :returns: `str` prettified country text
    """

    iso3166 = countries.get(country)

    return flag.flagize(f'{iso3166.name} :{iso3166.alpha2}:')


def search_gdc(**kwargs: dict) -> dict:
    """
    Search the GDC

    :param kwargs: `dict` of GDC query parameters:
                   - bbox: `list` of minx, miny, maxx, maxy
                   - begin: `str` of begin datetime
                   - end: `str` of end datetime
                   - type_: record type
                   - topic: topic hierarchy
                   - sortby: sort property and direction (i.e. prop:D|A)
                     (default A)

    :returns: `dict` of results
    """

    params = dict()
    title_maxlen = 50

    kwargs2 = kwargs

    sortby = kwargs2.pop('sortby')
    _ = kwargs2.pop('type_')
    datetime_ = None
    sortby2 = None

    begin = kwargs2.pop('begin')
    end = kwargs2.pop('end')

    # if type is not None:
    #    params['type'] = type_

    LOGGER.debug('Detecting begin / end')
    if any([begin is not None, end is not None]):
        if begin is None:
            begin2 = '..'
        if end is not None:
            end2 = '..'
        datetime_ = f'{begin2}/{end2}'

    if datetime_ is not None:
        params['datetime'] = datetime_

    LOGGER.debug('Detecting sortby')
    if sortby is not None:
        if ':' in sortby:
            sortby2 = sortby
        else:
            sortby2 = f'{sortby}:A'
    if sortby2 is not None:
        params['sortby'] = sortby2

    LOGGER.debug('Detecting all other query parameters')
    for key, value in kwargs2.items():
        if value is not None:
            if key == 'bbox':
                params['bbox'] = ','.join(str(t) for t in value)
            else:
                params[key] = value

    LOGGER.debug(f'query parameters: {params}')

    url = f'{GDC_URL}/items'
    response = requests.get(url, params=params)
    LOGGER.debug(f'URL: {response.url}')

    if not response.ok:
        LOGGER.warning(f'ERROR: {response.text}')
        return

    response_json = response.json()

    output = {
        'results': response_json['numberMatched'],
        'records': []
    }

    LOGGER.debug('Building up results')
    for item in response_json['features']:
        country, centre_id = get_country_and_centre(item['id'])

        output['fields'] = [
            'id',
            'centre',
            'title',
            'topic',
            'data policy'
        ]

        if len(item['properties']['title']) > title_maxlen:
            title_short = f"{item['properties']['title'][:title_maxlen]}..."
        else:
            title_short = item['properties']['title']

        try:
            output['records'].append((
                item['id'],
                centre_id,
                title_short,
                item['properties']['wmo:topicHierarchy'],
                item['properties']['wmo:dataPolicy']['name']
            ))
        except KeyError as err:
            LOGGER.debug(f"Record {item['id']} missing field: {err}")

    return output


def get_gdc_record(identifier: str) -> dict:
    """
    Get GDC record by identifier

    :param identifier: record identifier

    :returns: `dict` of record summary
    """

    url = f'{GDC_URL}/items/{identifier}'

    response = requests.get(url)
    LOGGER.debug(f'URL: {response.url}')

    if not response.ok:
        LOGGER.warning(f'ERROR: {response.text}')
        return

    return response.json()


@click.command()
@click.pass_context
@cli_option_verbosity
@click.option('--bbox', '-b', help='Bounding box filter')
@click.option('--query', '-q', 'q', help='Full text query')
def search(ctx, type_='dataset', begin=None, end=None, q=None,
           bbox=[], topic=None, sortby=None, verbosity='NOTSET'):
    """Search the WIS2 GDC"""

    if bbox:
        bbox2 = [float(i) for i in bbox.split(',')]
    else:
        bbox2 = bbox

    params = dict(
        type_=type_,
        begin=begin,
        end=end,
        q=q,
        bbox=bbox2,
        topic=topic,
        sortby=sortby
    )

    click.echo('\nQuerying WIS2 GDC 🗃️ ...\n')
    results = search_gdc(**params)

    if results is None:
        raise click.ClickException('Could not query catalogue')

    count = results['results']

    click.echo(f"Results: {results['results']} record{'s'[:count^1]}")

    if count == 0:
        return

    pt = PrettyTable()
    pt.field_names = results['fields']
    pt.align = 'l'

    for record in results['records']:
        pt.add_row(record)

    click.echo(pt.get_string())


@click.command()
@click.pass_context
@cli_option_verbosity
@click.argument('identifier')
def get(ctx, identifier, verbosity):
    """Get a WIS2 GDC record by identifier"""

    click.echo('\nQuerying WIS2 GDC 🗃️ ...\n')

    skip_rels = ['root', 'self', 'alternate', 'collection']

    result = get_gdc_record(identifier)

    if result is None:
        raise click.ClickException('Record identifier not found')

    country, centre_id = get_country_and_centre(result['id'])
    country = get_country_prettified(country)

    click.echo(f"Record: {result['properties']['title']}\n")
    click.echo(f"\tID: {result['id']}\n")
    click.echo(f"\tCountry: {country}\n")
    click.echo(f"\tCentre: {centre_id}\n")
    click.echo(f"\tTopic: {result['properties']['wmo:topicHierarchy']}\n")
    click.echo(f"\tData policy: {result['properties']['wmo:dataPolicy']['name']}\n")  # noqa

    description = '\n'.join(wrap(result['properties']['description']))
    description = indent(description, '\t').strip()

    click.echo(f'\tDescription: {description}\n')

    click.echo('\tLinks')

    for link in result['links']:
        if link['rel'] not in skip_rels:
            click.echo(f"\t\t{link['href']}")

    click.echo("\n")
