# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#          Ján Osuský <jan.osusky@iblsoft.com>
#
# Copyright (c) 2021 Tom Kralidis
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

import json
import unittest
from pywiscat.wis1.util import (group_by_originator)
from pywiscat.wis1.report import (group_search_results_by_organization)


class WISCatalogueUtilTest(unittest.TestCase):
    """WIS Catalogue tests"""

    def setUp(self):
        """setup test fixtures, etc."""
        pass

    def tearDown(self):
        """return to pristine state"""
        pass

    def test_group_by_originator(self):
        """Simple Tests of grouping"""

        with open('tests/data/small_list.json', 'r', encoding='utf-8') as file_list_json:
            file_list = json.load(file_list_json)
            results = group_by_originator(file_list)
            self.assertEqual(results['ECMWF'], 2)

    def test_term_by_originator(self):
        """Simple Tests of grouping for a term"""

        results = group_search_results_by_organization('tests/data/', 'grib')
        self.assertEqual(results['ECMWF'], 4)


if __name__ == '__main__':
    unittest.main()
