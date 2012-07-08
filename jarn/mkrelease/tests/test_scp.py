import unittest

from jarn.mkrelease.scp import SCP


class HasHostTests(unittest.TestCase):

    def test_simple(self):
        scp = SCP()
        self.assertEqual(scp.has_host('foo:bar'), True)

    def test_slash(self):
        scp = SCP()
        self.assertEqual(scp.has_host('foo:bar/baz'), True)

    def test_no_colon(self):
        scp = SCP()
        self.assertEqual(scp.has_host('foo/bar/baz'), False)

    def test_slash_before_colon(self):
        scp = SCP()
        self.assertEqual(scp.has_host('foo/bar:baz'), False)


class JoinTests(unittest.TestCase):

    def test_simple(self):
        scp = SCP()
        self.assertEqual(scp.join('foo:', 'bar'), 'foo:bar')

    def test_slash(self):
        scp = SCP()
        self.assertEqual(scp.join('foo:/', 'bar'), 'foo:/bar')

    def test_inserted_slash(self):
        scp = SCP()
        self.assertEqual(scp.join('foo:/bar', 'baz'), 'foo:/bar/baz')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

