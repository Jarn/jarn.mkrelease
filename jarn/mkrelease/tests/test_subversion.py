import unittest
import shutil

from os.path import join

from jarn.mkrelease.scm import Subversion

from jarn.mkrelease.testing import SubversionSetup
from jarn.mkrelease.testing import TestProcess
from jarn.mkrelease.testing import quiet


class ValidUrlTests(unittest.TestCase):

    def setUp(self):
        self.scm = Subversion()

    def testSvnUrl(self):
        pkgurl = 'svn://'
        self.assertEqual(self.scm.is_valid_url(pkgurl), True)

    def testSvnSshUrl(self):
        pkgurl = 'svn+ssh://'
        self.assertEqual(self.scm.is_valid_url(pkgurl), True)

    def testHttpUrl(self):
        pkgurl = 'http://'
        self.assertEqual(self.scm.is_valid_url(pkgurl), True)

    def testHttpsUrl(self):
        pkgurl = 'https://'
        self.assertEqual(self.scm.is_valid_url(pkgurl), True)

    def testFileUrl(self):
        pkgurl = 'file://'
        self.assertEqual(self.scm.is_valid_url(pkgurl), True)

    def testBadProtocol(self):
        pkgurl = 'ftp://'
        self.assertEqual(self.scm.is_valid_url(pkgurl), False)

    def testEmptyString(self):
        pkgurl = ''
        self.assertEqual(self.scm.is_valid_url(pkgurl), False)


class ValidSandboxTests(SubversionSetup):

    def testSandbox(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_sandbox('testpackage'), True)

    def testNotExists(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_sandbox('foo'), False)

    def testNotADir(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_sandbox(join('testpackage', 'setup.py')), False)

    def testNotACheckout(self):
        scm = Subversion()
        shutil.rmtree(join(self.packagedir, '.svn'))
        self.assertEqual(scm.is_valid_sandbox('testpackage'), False)


class UrlFromSandboxTests(SubversionSetup):

    def testGetUrl(self):
        scm = Subversion()
        self.assertEqual(scm.get_url_from_sandbox('testpackage'),
                         'https://svn.jarn.com/personal/stefan/testpackage/trunk')

    def testGetAnotherUrl(self):
        scm = Subversion()
        self.assertEqual(scm.get_url_from_sandbox(join('testpackage', 'testpackage')),
                         'https://svn.jarn.com/personal/stefan/testpackage/trunk/testpackage')

    @quiet
    def testBadSandbox(self):
        scm = Subversion(TestProcess(rc=1, lines=[]))
        self.assertRaises(SystemExit, scm.get_url_from_sandbox, '')

    @quiet
    def testSuccessButNoLines(self):
        scm = Subversion(TestProcess(rc=0, lines=[]))
        self.assertRaises(SystemExit, scm.get_url_from_sandbox, '')


class CheckinSandboxTests(SubversionSetup):

    def testCheckin(self):
        scm = Subversion(TestProcess(rc=0, lines=['Created revision r564726.']))
        self.assertEqual(scm.checkin_sandbox('', '', '', ''), 0)

    @quiet
    def testCheckinFailure(self):
        scm = Subversion(TestProcess(rc=1, lines=[]))
        self.assertRaises(SystemExit, scm.checkin_sandbox, '', '', '', '')


class CheckoutUrlTests(SubversionSetup):

    def testCheckout(self):
        scm = Subversion(TestProcess(rc=0, lines=['Checked out revision r453625.']))
        self.assertEqual(scm.checkout_url('', ''), 0)

    @quiet
    def testCheckoutFailure(self):
        scm = Subversion(TestProcess(rc=1, lines=[]))
        self.assertRaises(SystemExit, scm.checkout_url, '', '')


class TagIdTests(SubversionSetup):

    def testTagIdFromTrunk(self):
        scm = Subversion()
        self.assertEqual(scm.get_tag_id(self.packagedir, '1.0'),
                         'https://svn.jarn.com/personal/stefan/testpackage/tags/1.0')

    def testTagIdFromBranch(self):
        url = 'https://svn.jarn.com/personal/stefan/testpackage/branches/1.x'
        scm = Subversion(TestProcess(rc=0, lines=['', 'URL: '+url]))
        self.assertEqual(scm.get_tag_id(self.packagedir, '1.0'),
                         'https://svn.jarn.com/personal/stefan/testpackage/tags/1.0')

    def testTagIdFromTag(self):
        url = 'https://svn.jarn.com/personal/stefan/testpackage/tags/1.0c2'
        scm = Subversion(TestProcess(rc=0, lines=['', 'URL: '+url]))
        self.assertEqual(scm.get_tag_id(self.packagedir, '1.0'),
                         'https://svn.jarn.com/personal/stefan/testpackage/tags/1.0')

    @quiet
    def testTagIdFromBadUrl(self):
        url = 'https://svn.jarn.com/personal/stefan/testpackage'
        scm = Subversion(TestProcess(rc=0, lines=['', 'URL: '+url]))
        self.assertRaises(SystemExit, scm.get_tag_id, self.packagedir, '1.0')


class TagExistsTests(SubversionSetup):

    def testTagExists(self):
        scm = Subversion(TestProcess(rc=0, lines=['foo.py', 'bar.py']))
        self.assertEqual(scm.tag_exists('', ''), True)

    def testTagDoesNotExist(self):
        scm = Subversion(TestProcess(rc=1, lines=[]))
        self.assertEqual(scm.tag_exists('', ''), False)


class CreateTagTests(SubversionSetup):

    def testCreateTag(self):
        def func(cmd):
            if cmd.startswith('svn info'):
                return 0, ['', 'URL: https://svn.jarn.com/personal/stefan/testpackage/trunk']
            elif cmd.startswith('svn copy'):
                return 0, []

        scm = Subversion(TestProcess(func=func))
        self.assertEqual(scm.create_tag('', '', '', '', ''), 0)

    @quiet
    def testBadSandbox(self):
        def func(cmd):
            if cmd.startswith('svn info'):
                return 1, []

        scm = Subversion(TestProcess(func=func))
        self.assertRaises(SystemExit, scm.create_tag, '', '', '', '', '')

    @quiet
    def testBadCopy(self):
        def func(cmd):
            if cmd.startswith('svn info'):
                return 0, ['', 'URL: https://svn.jarn.com/personal/stefan/testpackage/trunk']
            elif cmd.startswith('svn copy'):
                return 1, []

        scm = Subversion(TestProcess(func=func))
        self.assertRaises(SystemExit, scm.create_tag, '', '', '', '', '')

