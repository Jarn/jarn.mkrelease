from __future__ import print_function

import unittest
import sys
import os

from os.path import join

from jarn.mkrelease.testing import JailSetup
from jarn.mkrelease.testing import MercurialSetup
from jarn.mkrelease.testing import MockProcess
from jarn.mkrelease.testing import quiet


class JailSetupTestCase(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        # Create some dirs
        os.mkdir('foo')
        os.mkdir(join('foo', 'bar'))

    def dummyTest(self):
        self.fail()

    def pushingTest(self):
        self.dirstack.push('foo')
        self.dirstack.push('bar')

    def doomingTest(self):
        delattr(self, 'dirstack')
        delattr(self, 'tempdir')


class JailSetupTests(unittest.TestCase):

    def setUp(self):
        # Save cwd
        self.cwd = os.getcwd()

    def testSetUp(self):
        test = JailSetupTestCase('dummyTest')
        test.setUp()
        # A temporary directory has been created
        self.assertTrue(os.path.isdir(test.tempdir))
        # And it is the current working directory
        self.assertEqual(test.tempdir, os.getcwd())

    def testTearDown(self):
        test = JailSetupTestCase('dummyTest')
        test.setUp()
        test.tearDown()
        # The temporary directory has been removed
        self.assertFalse(os.path.exists(test.tempdir))
        # And we are back in the directory we started in
        self.assertEqual(self.cwd, os.getcwd())

    def testFailingTest(self):
        test = JailSetupTestCase('dummyTest')
        suite = unittest.TestSuite((test,))
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(len(result.errors), 0)
        # The temporary directory has been removed
        self.assertFalse(os.path.exists(test.tempdir))
        # And we are back in the directory we started in
        self.assertEqual(self.cwd, os.getcwd())

    def testUnrollDirStack(self):
        suite = unittest.makeSuite(JailSetupTestCase, 'pushingTest')
        result = unittest.TestResult()
        suite.run(result)
        # We are back in the directory we started in
        self.assertEqual(self.cwd, os.getcwd())

    def testDestroyedFixture(self):
        suite = unittest.makeSuite(JailSetupTestCase, 'doomingTest')
        result = unittest.TestResult()
        suite.run(result)
        # We are NOT back in the directory we started in. That's expected,
        # but once we get here we know we did at least not blow up; which
        # is the point of this test.
        self.assertNotEqual(self.cwd, os.getcwd())


class PackageSetupTestCase(MercurialSetup):

    def dummyTest(self):
        self.fail()


class PackageSetupTests(unittest.TestCase):

    def testSetUp(self):
        test = PackageSetupTestCase('dummyTest')
        test.setUp()
        self.assertEqual(os.listdir(test.tempdir), ['testpackage'])

    def testTearDown(self):
        test = PackageSetupTestCase('dummyTest')
        test.setUp()
        test.tearDown()
        self.assertFalse(os.path.exists(test.tempdir))


class MockProcessTests(unittest.TestCase):

    def testPopenSuccess(self):
        process = MockProcess(rc=0, lines=[])
        self.assertEqual(process.popen(''), (0, []))

    def testPopenFailure(self):
        process = MockProcess(rc=1, lines=[])
        self.assertEqual(process.popen(''), (1, []))

    def testPopenLines(self):
        process = MockProcess(rc=0, lines=['these', 'are', '4', 'lines'])
        self.assertEqual(process.popen(''), (0, ['these', 'are', '4', 'lines']))

    def testSystemSuccess(self):
        process = MockProcess(rc=0, lines=[])
        self.assertEqual(process.system(''), 0)

    def testSystemFailure(self):
        process = MockProcess(rc=1, lines=[])
        self.assertEqual(process.system(''), 1)

    def testPipeSuccess(self):
        process = MockProcess(rc=0, lines=['these', 'are', '4', 'lines'])
        self.assertEqual(process.pipe(''), 'these')

    def testPipeFailure(self):
        process = MockProcess(rc=1, lines=['these', 'are', '4', 'lines'])
        self.assertEqual(process.pipe(''), '')

    def testPipeNoLines(self):
        process = MockProcess(rc=0, lines=[])
        self.assertEqual(process.pipe(''), '')

    def testOsSystemSuccess(self):
        process = MockProcess(rc=0, lines=[])
        self.assertEqual(process.os_system(''), 0)

    def testOsSystemFailure(self):
        process = MockProcess(rc=1, lines=[])
        self.assertEqual(process.os_system(''), 1)


class QuietTests(unittest.TestCase):

    @quiet
    def testQuiet(self):
        print('This should not show')
        print('This should not show either', file=sys.stderr)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

