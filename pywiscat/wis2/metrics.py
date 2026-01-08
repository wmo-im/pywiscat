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

from enum import Enum
from glob import glob
import json
import logging

import click
from pywcmp.wcmp2.kpi import WMOCoreMetadataProfileKeyPerformanceIndicators

from pywiscat.cli_helpers import cli_option_verbosity

LOGGER = logging.getLogger(__name__)


class DataPolicy(Enum):
    core: 'core'
    recommended: 'recommended'


def get_centre_id(identifier: str) -> str:
    """
    Derive centre identifier from a WCMP2 id

    :param identifier: `str` of WCMP2 id

    :returns: `str` of centre identifier
    """

    return identifier.split(':')[3]


def analyze_data_policy(data_policy: DataPolicy, archive_dir: str) -> dict:
    """
    Analyze archive for data policy

    :param data_policy: `str` of data policy (core or recommended)
    :param archive_dir: `str` of archive directory path

    :returns: `dict` of analysis, by centre identifier
    """

    report = {}

    LOGGER.debug(f'Analyzing {archive_dir} for {data_policy} records')
    for f in glob(f'{archive_dir}/*.json'):
        with open(f) as fh:
            wcmp2 = json.load(fh)
            centre_id = get_centre_id(wcmp2['id'])

            data_policy2 = wcmp2['properties']['wmo:dataPolicy']
            if data_policy2 == data_policy:
                if centre_id not in report:
                    report[centre_id] = 1
                else:
                    report[centre_id] += 1

    return dict(sorted(report.items()))


def analyze_earth_system_discipline(archive_dir: str) -> dict:
    """
    Analyze archive for Earth system discipline

    :param archive_dir: `str` of archive directory path

    :returns: `dict` of analysis, by centre identifier
    """

    report = {}

    LOGGER.debug(f'Analyzing {archive_dir} for Earth system disciplines')
    for f in glob(f'{archive_dir}/*.json'):
        with open(f) as fh:
            wcmp2 = json.load(fh)
            centre_id = get_centre_id(wcmp2['id'])

            for theme in wcmp2['properties']['themes']:
                if theme.get('scheme') == 'https://codes.wmo.int/wis/topic-hierarchy/earth-system-discipline':  # noqa
                    for concept in theme.get('concepts', []):
                        id_ = concept.get('id')
                        LOGGER.debug(f'concept: {id_}')

                        if centre_id not in report:
                            report[centre_id] = {
                                id_: 1
                            }
                        else:
                            if id_ not in report[centre_id]:
                                report[centre_id][id_] = 1
                            else:
                                report[centre_id][id_] += 1

    return dict(sorted(report.items()))


def analyze_kpi(centre_id: str, archive_dir: str) -> dict:
    """
    Analyze archive for Key Performance Indicators (KPI)

    :param archive_dir: `str` of centre identifier
    :param archive_dir: `str` of archive directory path

    :returns: `dict` of analysis, by centre identifier
    """

    LOGGER.debug(f'Analyzing KPIs for {centre_id}')
    report = {
        centre_id: {
            'kpi_percentage_average': 0,
            'kpi_percentage_over80_total': 0,
            'scoring': {}
        }
    }

    for f in glob(f'{archive_dir}/*{centre_id}*.json'):
        with open(f) as fh:
            wcmp2 = json.load(fh)

            kpis = WMOCoreMetadataProfileKeyPerformanceIndicators(wcmp2)
            results = kpis.evaluate()
            report[centre_id]['scoring'][wcmp2['id']] = results['summary']['percentage']  # noqa

    kpi_values = report[centre_id]['scoring'].values()
    total = sum(kpi_values)
    average = total / len(report[centre_id]['scoring'])
    report[centre_id]['kpi_percentage_average'] = average

    over80_total = sum(1 for value in kpi_values if value > 80)
    report[centre_id]['kpi_percentage_over80_total'] = over80_total

    return dict(sorted(report.items()))


@click.group()
def metrics():
    """Run metrics against a WIS2 GDC"""

    pass


@click.command()
@click.pass_context
@click.argument('archive_dir')
@cli_option_verbosity
def core(ctx, archive_dir, verbosity):
    """Analyze core records"""

    report = analyze_data_policy('core', archive_dir)
    click.echo(json.dumps(report, indent=4))


@click.command()
@click.pass_context
@click.argument('archive_dir')
@cli_option_verbosity
def recommended(ctx, archive_dir, verbosity):
    """Analyze recommended records"""

    report = analyze_data_policy('recommended', archive_dir)
    click.echo(json.dumps(report, indent=4))


@click.command()
@click.pass_context
@click.argument('archive_dir')
@cli_option_verbosity
def earth_system_discipline(ctx, archive_dir, verbosity):
    """Analyze Earth system disciplines"""

    report = analyze_earth_system_discipline(archive_dir)
    click.echo(json.dumps(report, indent=4))


@click.command()
@click.pass_context
@click.argument('centre_id')
@click.argument('archive_dir')
@cli_option_verbosity
def kpi(ctx, centre_id, archive_dir, verbosity):
    """Analyze Key Performance Indicators (KPIs)"""

    report = analyze_kpi(centre_id, archive_dir)
    click.echo(json.dumps(report, indent=4))


metrics.add_command(core)
metrics.add_command(recommended)
metrics.add_command(earth_system_discipline)
metrics.add_command(kpi)
