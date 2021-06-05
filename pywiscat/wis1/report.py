# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2021 Tom Kralidis
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
import os
from lxml import etree

import click

from pywiscat.cli_helpers import cli_callbacks, cli_option_directory

LOGGER = logging.getLogger(__name__)


@click.group()
def report():
    """Reporting functions"""
    pass


NAMESPACES = {
    'gco': 'http://www.isotc211.org/2005/gco',
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gml': 'http://www.opengis.net/gml/3.2',
    'gmx': 'http://www.isotc211.org/2005/gmx',
    'gts': 'http://www.isotc211.org/2005/gts',
    'xlink': 'http://www.w3.org/1999/xlink'
}


def group_search_results_by_organization(directory: str, terms: list) -> dict:
    """
    Searches directory tree of metadata for matching search terms and
    and groups by organization

    :param directory: directory to metadata files
    :param terms: list of terms

    :returns: dict of results grouped by organization
    """

    matches = []
    matches_by_org = {}

    LOGGER.debug(f'Walking directory {directory}')
    for root, _, files in os.walk(directory):
        for name in files:
            filename = f'{root}/{name}'
            LOGGER.debug(f'filename: {filename}')

            if not filename.endswith('.xml'):
                continue

            e = etree.parse(filename)
            anytext = ' '.join(
                [value.strip() for value in e.xpath('//text()')])

            if all(term.lower() in anytext.lower() for term in terms):
                LOGGER.debug('Found match, extracting organization')
                matches.append(filename)
                try:
                    for contact in e.xpath('//gmd:CI_ResponsibleParty', namespaces=NAMESPACES):  # noqa
                        if contact.xpath("//gmd:CI_RoleCode[@codeListValue='pointOfContact']", namespaces=NAMESPACES):  # noqa
                            org_name = contact.xpath('//gmd:organisationName/gco:CharacterString/text()', namespaces=NAMESPACES)  # noqa
                            if org_name:
                                if org_name[0] in matches_by_org:
                                    LOGGER.debug('Adding to existing key')
                                    matches_by_org[org_name[0]] += 1
                                else:
                                    LOGGER.debug('Adding to new key')
                                    matches_by_org[org_name[0]] = 1
                except Exception as err:
                    LOGGER.error(f'Error analyzing {filename}: {err}')

    LOGGER.debug(f'Matching records ({len(matches)}: {matches}')
    return matches_by_org


@click.command()
@click.pass_context
@cli_callbacks
@cli_option_directory
@click.option('--term', '-t', 'terms', multiple=True, required=True)
def terms_by_org(ctx, terms, directory, verbosity):
    """Analyze term searches by organization"""

    click.echo(f'Analyzing records in {directory} for terms {terms}')
    results = group_search_results_by_organization(directory, terms)

    if results:
        click.echo(json.dumps(results, indent=4))
    else:
        click.echo('No results')


report.add_command(terms_by_org)
