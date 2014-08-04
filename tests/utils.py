# -*- coding: utf-8  -*-
#
# (C) Pywikibot team, 2013-2014
#
# Distributed under the terms of the MIT license.
#
from __future__ import print_function
__version__ = '$Id$'
#
import time
import sys
try:
    # Unittest2 is a backport of python 2.7s unittest module to python 2.6
    # Trying to import unittest2 has to happen first because 2.6 does have a
    # unittest module in the standard library but that doesn't support all the
    # features of the one found in python 2.7, so importing unittest first and
    # then trying to figure out if it supports the features used would mean
    # checking the module contents etc. Just catching an ImportError once is
    # much easier.
    import unittest2 as unittest
except ImportError:
    import unittest

import pywikibot

# Number of seconds each test may consume before a note is added after the test.
test_duration_warning_interval = 10


def collector():
    # This test collector loads tests from the `tests` directory in files
    # matching the pattern `*tests.py`. This gets used by `setup.py test` when
    # running on Python 2.6 to use the unittest2 test runner instead of the
    # unittest one.
    return unittest.loader.defaultTestLoader.discover("tests", "*tests.py")

from tests import patch_request, unpatch_request


class BaseTestCase(unittest.TestCase):

    """Base class for all test cases.

    Adds timing info to stdout.
    """

    def assertType(self, obj, cls):
        """Assert that obj is an instance of type cls"""
        return self.assertTrue(isinstance(obj, cls))

    def setUp(self):
        self.test_start = time.time()

    def tearDown(self):
        self.test_completed = time.time()
        duration = self.test_completed - self.test_start

        if duration > test_duration_warning_interval:
            print(' %0.3fs' % duration, end=' ')
            sys.stdout.flush()


class NoSiteTestCase(BaseTestCase):

    """Test cases not connected to a Site object.

    Do not use this for mock Site objects.

    Never set a class or instance variable called 'site'
    As it will prevent tests from executing when invoked as:
    $ nosetests -a '!site' -v
    """

    def setUp(self):
        self.old_Site_lookup_method = pywikibot.Site
        pywikibot.Site = lambda *args: self.fail('%s: Site() not permitted'
                                                 % self.__class__.__name__)

        super(NoSiteTestCase, self).setUp()

    def tearDown(self):
        super(NoSiteTestCase, self).tearDown()

        pywikibot.Site = self.old_Site_lookup_method


class SiteTestCase(BaseTestCase):

    """Test cases connected to a Site object.

    Do not use this for mock Site objects.
    """

    site = True


class CachedTestCase(SiteTestCase):

    """Aggressively cached API test cases.

    Patches pywikibot.data.api to aggressively cache
    API responses.
    """

    def setUp(self):
        patch_request()

        super(CachedTestCase, self).setUp()

    def tearDown(self):
        super(CachedTestCase, self).tearDown()

        unpatch_request()

PywikibotTestCase = CachedTestCase
