# THIS SHOULD BE DOCTESTS

from jarn.mkrelease.mkrelease import main
from jarn.mkrelease.testing import SubversionSetup


class Tests(SubversionSetup):

    def mkrelease(self, args):
        return main(args)

    def testSimpleRelease(self):
        #self.mkrelease('-CT -d epy testpackage'.split())
        pass

