# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#          Ján Osuský <jan.osusky@iblsoft.com>
#
# Copyright (c) 2023 Tom Kralidis
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

import json
import logging
import os

import click

from pywcmp.kpi import wcmp_kpis1
from pywcmp.util import parse_wcmp

from pywiscat.cli_helpers import cli_callbacks
from pywiscat.wis1.util import (create_file_list, search_files_by_term, group_by_originator)

LOGGER = logging.getLogger(__name__)


@click.group()
def report():
    """Reporting functions"""
    pass


def group_search_results_by_organization(directory: str, terms: list, group_by_authority: bool) -> dict:

    """
    Searches directory tree of metadata for matching search terms and
    and groups by organization

    :param directory: directory to metadata files
    :param terms: list of terms

    :returns: dict of results grouped by organization
    """

    matches = search_files_by_term(directory, terms)
    matches_by_org = group_by_originator(matches, group_by_authority)

    return matches_by_org


@click.command()
@click.pass_context
@cli_callbacks
@click.option('--directory', '-d', required=False,
              help='Directory with metadata files to process',
              type=click.Path(resolve_path=True, file_okay=False))
@click.option('--term', '-t', 'terms', multiple=True, required=True,
              help='Terms (sub-strings) to be searched in the metadata, case insensitive')
@click.option('--file-list', '-f', 'file_list_file',
              type=click.Path(exists=True, resolve_path=True), required=False,
              help='File containing JSON list with metadata files to process, alternative to "-d"')
@click.option('--group', '-g', 'group_by_authority', is_flag=True, default=False,
              help='Group organizations by citation authority in the file identifier')
def terms_by_org(ctx, terms, directory, file_list_file, group_by_authority, verbosity):
    """Analyze term searches by organization"""

    if file_list_file is None and directory is None:
        raise click.UsageError('Missing --file-list or --directory option')

    results = {}
    if not file_list_file:
        click.echo(f'Analyzing records in {directory} for terms {terms}')
        results = group_search_results_by_organization(directory, terms, group_by_authority)
    else:
        file_list = []
        with open(file_list_file, "r", encoding="utf-8") as file_list_json:
            try:
                file_list = json.load(file_list_json)
            except Exception as err:
                LOGGER.error(f'Failed to read file list {file_list_file}: {err}')
                return
            results = group_by_originator(file_list, group_by_authority)

    if results:
        click.echo(json.dumps(results, indent=4))
    else:
        click.echo('No results')


@click.command()
@click.pass_context
@cli_callbacks
@click.option('--directory', '-d', required=False,
              help='Directory with metadata files to process',
              type=click.Path(resolve_path=True, file_okay=False))
@click.option('--file-list', '-f', 'file_list_file',
              type=click.Path(exists=True, resolve_path=True), required=False,
              help='File containing JSON list with metadata files to process, alternative to "-d"')
@click.option('--group', '-g', 'group_by_authority', is_flag=True, default=False,
              help='Group organizations by citation authority in the file identifier')
def records_by_org(ctx, directory, file_list_file, group_by_authority, verbosity):
    """Report number of records by organization / originator"""

    if file_list_file is None and directory is None:
        raise click.UsageError('Missing --file-list or --directory option')

    results = {}
    if not file_list_file:
        click.echo(f'Analyzing records in {directory}')
        file_list = create_file_list(directory)
        results = group_by_originator(file_list, group_by_authority)
    else:
        file_list = []
        with open(file_list_file, "r", encoding="utf-8") as file_list_json:
            try:
                file_list = json.load(file_list_json)
            except Exception as err:
                LOGGER.error(f'Failed to read file list {file_list_file}: {err}')
                return
            results = group_by_originator(file_list, group_by_authority)

    if results:
        click.echo(json.dumps(results, indent=4))
    else:
        click.echo('No results')


@click.command(short_help='KPI assessment of metadata files')
@click.pass_context
@cli_callbacks
@click.option('--directory', '-d', required=False,
              help='Directory with metadata files to process',
              type=click.Path(resolve_path=True, file_okay=False))
@click.option('--file-list', '-f', 'file_list_file',
              type=click.Path(exists=True, resolve_path=True), required=False,
              help='File containing JSON list with metadata files to process, alternative to "-d"')
@click.option('--kpi', '-k', default=0, help='KPI to run, default is all')
@click.option('--output-format', '-o', 'output_format', default='brief',
              type=click.Choice(['brief', 'summary', 'full'], case_sensitive=False),
              help='Output format of the KPI results')
@click.option('--group', '-g', 'group_by_authority', is_flag=True, default=False,
              help='Group results by citation authority in the file identifier')
def kpi(ctx, directory, file_list_file, group_by_authority, kpi, output_format, verbosity):
    """Runs kpi assessment on all metadata files in a directory or list"""

    if file_list_file is None and directory is None:
        raise click.UsageError('Missing --file-list or --directory option')

    results = {}
    file_list = []
    if not file_list_file:
        click.echo(f'Analyzing records in {directory}')
        file_list = create_file_list(directory)
    else:
        with open(file_list_file, "r", encoding="utf-8") as file_list_json:
            try:
                file_list = json.load(file_list_json)
            except Exception as err:
                LOGGER.error(f'Failed to read file list {file_list_file}: {err}')
                return

    for file_path in file_list:
        parent_path, filename = os.path.split(file_path)
        LOGGER.debug(f'Analyzing: {filename}')

        try:
            exml = parse_wcmp(file_path)
        except Exception as err:
            raise click.ClickException(err)

        kpis = wcmp_kpis1(exml)

        try:
            kpis_results = kpis.evaluate(kpi)
        except ValueError as err:
            raise click.UsageError(f'Invalid KPI {kpi}: {err}')

        if kpi == 0:
            LOGGER.info(f'{kpis.identifier}: {kpis_results["summary"]["percentage"]}% {kpis_results["summary"]["grade"]}')
        else:
            selected_kpi = f'kpi_{kpi:03}'
            LOGGER.info(f'{kpis.identifier}: {kpis_results[selected_kpi]["percentage"]}%')

        if kpi == 0 and output_format == 'brief':
            results[file_path] = {
                'percentage': kpis_results['summary']['percentage'],
                'grade': kpis_results['summary']['grade'],
                'identifier': kpis.identifier
            }
        elif kpi == 0 and output_format == 'summary':
            results[file_path] = kpis_results['summary']
        elif output_format == 'brief':
            selected_kpi = f'kpi_{kpi:03}'
            results[file_path] = {
                'percentage': kpis_results[selected_kpi]['percentage'],
                'identifier': kpis.identifier
            }
        else:
            results[file_path] = kpis_results

    click.echo(json.dumps(results, indent=4))


report.add_command(terms_by_org)
report.add_command(records_by_org)
report.add_command(kpi)
