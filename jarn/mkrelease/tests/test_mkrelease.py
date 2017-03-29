# THIS SHOULD BE DOCTESTS
import unittest

from jarn.mkrelease.mkrelease import main
from jarn.mkrelease.testing import SubversionSetup


class Tests(SubversionSetup):

    def mkrelease(self, args):
        return main(args)

    def testSimpleRelease(self):
        #self.mkrelease('-CT -d epy testpackage'.split())
        pass


class MakeReleaseTests(unittest.TestCase):

    def test_create(self):
        from jarn.mkrelease.mkrelease import ReleaseMaker
        ReleaseMaker([])


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

