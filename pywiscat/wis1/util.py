# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#          Ján Osuský <jan.osusky@iblsoft.com>
#
# Copyright (c) 2021 Government of Canada
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

import logging
import math
import os
from lxml import etree

LOGGER = logging.getLogger(__name__)

NAMESPACES = {
    'gco': 'http://www.isotc211.org/2005/gco',
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gml': 'http://www.opengis.net/gml/3.2',
    'gmx': 'http://www.isotc211.org/2005/gmx',
    'gts': 'http://www.isotc211.org/2005/gts',
    'xlink': 'http://www.w3.org/1999/xlink'
}


def create_file_list(directory: str) -> list:
    """
    Searches directory tree of metadata for *.xml files

    :param directory: directory to metadata files

    :returns: list of file names
    """

    file_list = []

    LOGGER.debug(f'Walking directory {directory}')
    for root, _, files in os.walk(directory):
        for name in files:
            filename = f'{root}/{name}'

            if not filename.endswith('.xml'):
                continue

            file_list.append(filename)

    return file_list


def search_files_by_term(directory: str, terms: list) -> list:
    """
    Searches directory tree of metadata for files containing search terms

    :param directory: directory to metadata files
    :param terms: list of terms

    :returns: list of file names
    """

    matches = []

    match_count = 0
    file_count = 0
    file_list = create_file_list(directory)
    for filename in file_list:
        LOGGER.debug(filename)

        file_count += 1
        processed = math.floor(file_count * 100 / len(file_list))

        if not filename.endswith('.xml'):
            continue

        e = etree.parse(filename)
        anytext = ' '.join(
            [value.strip() for value in e.xpath('//text()')])

        if all(term.lower() in anytext.lower() for term in terms):
            match_count += 1
            LOGGER.debug(f'Found match #{match_count}, searched {processed}%')
            matches.append(filename)
        else:
            LOGGER.debug(f'No match found, searched {processed}%')

    LOGGER.debug(f'Found {len(matches)} matching metadata records.')
    return matches


def identifier(exml):
    """
    Helper function to derive a metadata record identifier

    :param exml: `etree.ElementTree` object

    :returns: metadata record identifier
    """

    xpath = '//gmd:fileIdentifier/gco:CharacterString/text()'

    return exml.xpath(xpath, namespaces=NAMESPACES)[0]


def citation_authority(file_identifier: str):
    """
    Helper function to extract citation authority (kind of originator center reverse DNS) from file identifier

    :param file_identifier: Identifier of the file (metadata document) to extract the authority from.

    :returns: citation authority, or empty string if the extraction failed
    """

    if file_identifier is not None:
        components = file_identifier.split(':')
        if len(components) > 3:
            return components[3]
    return ''


def group_by_originator(file_list: list, group_by_authority: bool) -> dict:
    """
    Processes the given file list (MD records) and groups them by originator/pointOfContact
    and optionally also by citation authority from the file identifier.

    :param file_list: list of MD XML files
    :param group_by_authority: whether to group the list by (citation) authority or not

    :returns: dict of results grouped by metadata originator
    """

    results_by_org = {}

    file_count = 0

    for file_path in file_list:

        parent_path, filename = os.path.split(file_path)
        LOGGER.debug(f'Analyzing: {filename}')

        exml = etree.parse(file_path)

        file_count += 1
        analyzed = math.floor(file_count * 100 / len(file_list))

        try:
            element_xpath = '//gmd:CI_ResponsibleParty'
            code_list_value_xpath = "gmd:role/gmd:CI_RoleCode[@codeListValue='pointOfContact']"
            found = False
            for contact in exml.xpath(element_xpath, namespaces=NAMESPACES):

                point_of_contact = contact.xpath(code_list_value_xpath, namespaces=NAMESPACES)
                if point_of_contact:
                    org_name = contact.xpath('gmd:organisationName/gco:CharacterString/text()', namespaces=NAMESPACES)  # noqa
                    LOGGER.debug(f'{contact.sourceline}: Found "{code_list_value_xpath}" with value "{org_name}"')
                    if org_name:
                        found = True
                        authority = citation_authority(identifier(exml)) if group_by_authority else None
                        if authority is not None and authority not in results_by_org:
                            results_by_org[authority] = {}
                        results = results_by_org if authority is None else results_by_org[authority]
                        if org_name[0] in results:
                            LOGGER.debug(f'{contact.sourceline}: Adding to existing key, analyzed {analyzed}%')
                            results[org_name[0]] += 1
                        else:
                            LOGGER.debug(f'{contact.sourceline}: Adding to new key, analyzed {analyzed}%')
                            results[org_name[0]] = 1
                        break
            if not found:
                LOGGER.info(f'No {element_xpath} with {code_list_value_xpath} found in {filename}, analyzed {analyzed}%')

        except Exception as err:
            LOGGER.error(f'Error analyzing {filename}: {err}')

    return results_by_org
