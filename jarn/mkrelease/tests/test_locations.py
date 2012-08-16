import unittest

from jarn.mkrelease.mkrelease import Locations


class defaults:
    distbase = ''
    distdefault = ''
    sign = False
    identity = ''
    push = False
    aliases = {}
    servers = {}


class HasHostTests(unittest.TestCase):

    def test_simple(self):
        locations = Locations(defaults)
        self.assertEqual(locations.has_host('foo:bar'), True)

    def test_slash(self):
        locations = Locations(defaults)
        self.assertEqual(locations.has_host('foo:bar/baz'), True)

    def test_no_colon(self):
        locations = Locations(defaults)
        self.assertEqual(locations.has_host('foo/bar/baz'), False)

    def test_slash_before_colon(self):
        locations = Locations(defaults)
        self.assertEqual(locations.has_host('foo/bar:baz'), False)


class JoinTests(unittest.TestCase):

    def test_simple(self):
        locations = Locations(defaults)
        self.assertEqual(locations.join('foo:', 'bar'), 'foo:bar')

    def test_slash(self):
        locations = Locations(defaults)
        self.assertEqual(locations.join('foo:/', 'bar'), 'foo:/bar')

    def test_inserted_slash(self):
        locations = Locations(defaults)
        self.assertEqual(locations.join('foo:/bar', 'baz'), 'foo:/bar/baz')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

