# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#          Ján Osuský <jan.osusky@iblsoft.com>
#
# Copyright (c) 2023 Tom Kralidis
# Copyright (c) 2021, IBL Software Engineering spol. s r. o.
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

import unittest

from pywiscat.wis2.catalogue import (
    get_country_and_centre_id, get_country_prettified)
from pywiscat.wis2.metrics import get_centre_id


class WISCatalogueUtilTest(unittest.TestCase):
    """WIS Catalogue tests"""

    def setUp(self):
        """setup test fixtures, etc."""
        pass

    def tearDown(self):
        """return to pristine state"""
        pass

    def test_get_centre_id(self):
        """test for centre-id detection from a WCMP2 ID"""

        wcmp2_id = 'urn:wmo:md:zm-zmd:core.surface-based-observations.synop'
        self.assertEqual(get_centre_id(wcmp2_id), 'zm-zmd')

    def test_get_country_and_centre_id(self):
        """test for country and centre-id detection from a WCMP2 ID"""

        wcmp2_id = 'urn:wmo:md:zm-zmd:core.surface-based-observations.synop'
        country, centre_id = get_country_and_centre_id(wcmp2_id)
        self.assertEqual(country, 'zm')
        self.assertEqual(centre_id, 'zm-zmd')

    def test_get_prettified_country(self):
        """test for country and centre-id detection from a WCMP2 ID"""

        country_prettified = get_country_prettified('zm')

        self.assertEqual(country_prettified, 'Zambia 🇿🇲')


if __name__ == '__main__':
    unittest.main()
