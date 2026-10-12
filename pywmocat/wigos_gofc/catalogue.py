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
from textwrap import indent, wrap

import click
from prettytable import PrettyTable
import requests

from pywmocat.cli_helpers import cli_option_verbosity
from pywmocat.env import WIGOS_GOFC_URL
from pywmocat.util import get_country_prettified

LOGGER = logging.getLogger(__name__)


def search(**kwargs: dict) -> dict:
    """
    Search the GOFC

    :param kwargs: `dict` of GOFC query parameters:
                   - q: `str` of full-text search
                   - country: `str` of country
                   - bbox: `list` of minx, miny, maxx, maxy
                   - begin: `str` of begin datetime
                   - end: `str` of end datetime
                   - type_: facility type
                   - limit: number of records to limit
                   - offset: startposition of result set
                   - sortby: sort property and direction (i.e. prop:D|A)
                     (default A)

    :returns: `dict` of results
    """

    params = {
        'f': 'json'
    }

    title_maxlen = 50

    kwargs2 = kwargs

    sortby = kwargs2.pop('sortby', None)
    _ = kwargs2.pop('type_', None)
    datetime_ = None

    begin = kwargs2.pop('begin', None)
    end = kwargs2.pop('end', None)

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
        params['sortby'] = sortby

    LOGGER.debug('Detecting all other query parameters')
    for key, value in kwargs2.items():
        if value is not None:
            if key == 'bbox':
                params['bbox'] = ','.join(str(t) for t in value)
            elif key == 'q':
                params['q'] = value.replace('/', '\\/')
            elif key == 'country':
                params['territories.territory'] = value
            else:
                params[key] = value

    params['f'] = 'json'

    LOGGER.debug(f'query parameters: {params}')

    url = f'{WIGOS_GOFC_URL}/items'
    response = requests.get(url, params=params)
    LOGGER.debug(f'URL: {response.url}')

    if not response.ok:
        LOGGER.debug(f'ERROR: {response.text}')
        return

    response_json = response.json()

    output = {
        'matched': response_json['numberMatched'],
        'returned': response_json['numberReturned'],
        'records': []
    }

    LOGGER.debug('Building up results')
    for item in response_json['features']:
        output['fields'] = [
            'id',
            'title',
            'facility type',
            'country',
            'WMO region',
            'number of observations'
        ]

        if len(item['properties']['title']) > title_maxlen:
            title_short = f"{item['properties']['title'][:title_maxlen]}..."
        else:
            title_short = item['properties']['title']

        country = get_country_prettified(
            item['properties']['territories'][0]['territory']['id'])

        try:
            output['records'].append((
                item['id'],
                title_short,
                item['properties']['facilityType']['id'],
                country,
                item['properties']['wmoRegion']['id'],
                len(item['properties']['observations'])
            ))
        except KeyError as err:
            LOGGER.debug(f"Record {item['id']} missing field: {err}")

    return output


def get(identifier: str) -> tuple:
    """
    Get GDC record by identifier

    :param identifier: record identifier

    :returns: `tuple` of URL and record
    """

    url = f'{WIGOS_GOFC_URL}/items/{identifier}'

    response = requests.get(url)
    LOGGER.debug(f'URL: {response.url}')

    if not response.ok:
        LOGGER.debug(f'ERROR: {response.text}')

    return response.url, response.json()


@click.command('search')
@click.pass_context
@click.option('--query', '-q', 'q', help='Full text query')
@click.option('--bbox', '-b', help='Bounding box filter')
@click.option('--country', '-co', 'country', help='Country')
@click.option('--begin', 'begin', help='Begin time (in RFC3339 format)')
@click.option('--end', 'end', help='End time (in RFC3339 format)')
@click.option('--sortby', '-s', 'sortby', help='Property to sort by')
@click.option('--limit', '-l', 'limit', type=int, default=500,
              help='number of records to limit')
@click.option('--offset', '-o', 'offset', type=int, default=0,
              help='startposition of result set')
@cli_option_verbosity
def search_(ctx, begin=None, end=None, q=None,
            bbox=[], sortby=None, country=None, limit=500, offset=0,
            verbosity='NOTSET'):
    """Search the WIGOS GOFC"""

    if bbox:
        bbox2 = [float(i) for i in bbox.split(',')]
    else:
        bbox2 = bbox

    params = dict(
        begin=begin,
        end=end,
        q=q,
        bbox=bbox2,
        sortby=sortby,
        limit=limit,
        offset=offset,
        country=country
    )

    click.echo(f'\nQuerying WIGOS GOFC 🗃️  {WIGOS_GOFC_URL} ...\n')
    results = search(**params)

    if results is None:
        raise click.ClickException('Could not query catalogue')

    count = results['matched']

    click.echo(f"Showing {results['returned']} of {results['matched']} record{'s'[:count^1]}")  # noqa

    if count == 0:
        return

    pt = PrettyTable()
    pt.field_names = results['fields']
    pt.align = 'l'

    for record in results['records']:
        pt.add_row(record)

    click.echo(pt.get_string())


@click.command('get')
@click.pass_context
@click.argument('identifier')
@cli_option_verbosity
def get_(ctx, identifier, verbosity):
    """Get a WIGOS GOFC record by identifier"""

    click.echo(f'\nQuerying WIGOS GOFC 🗃️  {WIGOS_GOFC_URL} ...\n')

    skip_rels = ['root', 'self', 'alternate', 'collection']

    url, result = get(identifier)

    if 'description' in result:
        raise click.ClickException(f'Record identifier {identifier} not found')

    click.echo(f"Record: {result['properties']['title']}\n")

    country = result['properties']['territories'][0]['territory']['id']
    country = get_country_prettified(country)

    click.echo(f"URL to full metadata: {url}\n")
    click.echo(f"\tID: {result['id']}\n")
    click.echo(f"\tFacility type: {result['properties']['facilityType']['id']}\n")  # noqa
    click.echo(f"\tWMO region: {result['properties']['wmoRegion']['id']}\n")
    click.echo(f"\tCountry: {country}\n")

    if result['properties'].get('description') is not None:
        description = '\n'.join(wrap(result['properties']['description']))
        description = indent(description, '\t').strip()
        click.echo(f'\tDescription: {description}\n')

    number_of_observations = len(result['properties']['observations'])
    click.echo(f'\tObservations ({number_of_observations}):')

    for obs in result['properties']['observations']:
        click.echo(f"\t\tObservation: {obs['observedProperty']['id']}")
        click.echo('\t\tProgram affiliations:')
        for pa in obs['programAffiliations']:
            click.echo(f"\t\t\t- {pa['programAffiliation']['id']}")

    click.echo('\tLinks:')

    for link in result['links']:
        if link['rel'] not in skip_rels:
            click.echo(f"\t\t- href: {link['href']}")

    click.echo('\n')
