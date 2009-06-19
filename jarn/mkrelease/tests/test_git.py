import unittest
import os

from os.path import join, isdir

from jarn.mkrelease.scm import Git

from jarn.mkrelease.process import Process

from jarn.mkrelease.testing import GitSetup
from jarn.mkrelease.testing import MockProcess
from jarn.mkrelease.testing import quiet


class ValidUrlTests(unittest.TestCase):

    def testGitUrl(self):
        scm = Git()
        self.assertEqual(scm.is_valid_url('git://'), True)

    def testRsyncUrl(self):
        scm = Git()
        self.assertEqual(scm.is_valid_url('rsync://'), True)

    def testSshUrl(self):
        scm = Git()
        self.assertEqual(scm.is_valid_url('ssh://'), True)

    def testHttpUrl(self):
        scm = Git()
        self.assertEqual(scm.is_valid_url('http://'), True)

    def testHttpsUrl(self):
        scm = Git()
        self.assertEqual(scm.is_valid_url('https://'), True)

    def testFileUrl(self):
        scm = Git()
        self.assertEqual(scm.is_valid_url('file://'), True)

    def testBadProtocol(self):
        scm = Git()
        self.assertEqual(scm.is_valid_url('svn://'), False)

    def testEmptyString(self):
        scm = Git()
        self.assertEqual(scm.is_valid_url(''), False)


class ValidSandboxTests(GitSetup):

    def testSandbox(self):
        scm = Git()
        self.assertEqual(scm.is_valid_sandbox(self.packagedir), True)

    def testNotExists(self):
        scm = Git()
        self.assertEqual(scm.is_valid_sandbox('foo'), False)

    def testNotADir(self):
        scm = Git()
        self.assertEqual(scm.is_valid_sandbox(join(self.packagedir, 'setup.py')), False)

    def testNotACheckout(self):
        scm = Git()
        self.destroy()
        self.assertEqual(scm.is_valid_sandbox(self.packagedir), False)

    @quiet
    def testCheckRaises(self):
        scm = Git()
        self.assertRaises(SystemExit, scm.check_valid_sandbox, 'foo')
        self.assertRaises(SystemExit, scm.check_valid_sandbox, join(self.packagedir, 'setup.py'))
        self.destroy()
        self.assertRaises(SystemExit, scm.check_valid_sandbox, self.packagedir)


class UrlFromSandboxTests(GitSetup):

    def testGetLocalUrl(self):
        scm = Git()
        self.assertEqual(scm.get_url_from_sandbox(self.packagedir), '')

    def testGetRemoteUrl(self):
        scm = Git()
        self.clone()
        self.assertEqual(scm.get_url_from_sandbox(self.clonedir), self.packagedir)

    def testBadSandbox(self):
        scm = Git()
        self.destroy()
        # Note: No SystemExit, just returns empty string
        self.assertEqual(scm.get_url_from_sandbox(self.packagedir), '')

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.get_url_from_sandbox, self.packagedir)


class RemoteSandboxTests(GitSetup):

    def testIsLocalSandbox(self):
        scm = Git()
        self.assertEqual(scm.is_remote_sandbox(self.packagedir), False)

    def testIsRemoteSandbox(self):
        scm = Git()
        self.clone()
        self.assertEqual(scm.is_remote_sandbox(self.clonedir), True)

    def testBadSandbox(self):
        scm = Git()
        self.destroy()
        # Note: No SystemExit, just returns False
        self.assertEqual(scm.is_remote_sandbox(self.packagedir), False)

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.is_remote_sandbox, self.packagedir)


class DirtySandboxTests(GitSetup):

    def testCleanSandbox(self):
        scm = Git()
        self.assertEqual(scm.is_dirty_sandbox(self.packagedir), False)

    def testModifiedFile(self):
        scm = Git()
        self.modify(self.packagedir)
        self.assertEqual(scm.is_dirty_sandbox(self.packagedir), True)

    def testRemovedFile(self):
        scm = Git()
        self.remove(self.packagedir)
        self.assertEqual(scm.is_dirty_sandbox(self.packagedir), True)

    def testDeletedButTrackedFile(self):
        scm = Git()
        self.delete(self.packagedir)
        # Note: The sandbox is reported as *dirty*
        self.assertEqual(scm.is_dirty_sandbox(self.packagedir), True)

    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        # Note: The sandbox is reported as clean
        self.assertEqual(scm.is_dirty_sandbox(self.packagedir), False)

    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        # Note: The sandbox is reported as clean
        self.assertEqual(scm.is_dirty_sandbox(self.packagedir), False)

    @quiet
    def testCheckRaises(self):
        scm = Git()
        self.modify(self.packagedir)
        self.assertRaises(SystemExit, scm.check_dirty_sandbox, self.packagedir)


class UncleanSandboxTests(DirtySandboxTests):

    def testCleanSandbox(self):
        scm = Git()
        self.assertEqual(scm.is_unclean_sandbox(self.packagedir), False)

    def testModifiedFile(self):
        scm = Git()
        self.modify(self.packagedir)
        self.assertEqual(scm.is_unclean_sandbox(self.packagedir), True)

    def testRemovedFile(self):
        scm = Git()
        self.remove(self.packagedir)
        self.assertEqual(scm.is_unclean_sandbox(self.packagedir), True)

    def testDeletedButTrackedFile(self):
        scm = Git()
        self.delete(self.packagedir)
        # Note: The sandbox is reported as *unclean*
        self.assertEqual(scm.is_unclean_sandbox(self.packagedir), True)

    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        # Note: The sandbox is reported as clean
        self.assertEqual(scm.is_unclean_sandbox(self.packagedir), False)

    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        # Note: The sandbox is reported as clean
        self.assertEqual(scm.is_unclean_sandbox(self.packagedir), False)

    @quiet
    def testCheckRaises(self):
        scm = Git()
        self.modify(self.packagedir)
        self.assertRaises(SystemExit, scm.check_unclean_sandbox, self.packagedir)


class UpdateSandboxTests(GitSetup):

    def testUpdateLocalSandbox(self):
        scm = Git()
        self.assertEqual(scm.update_sandbox(self.packagedir), 0)

    def testUpdateRemoteSandbox(self):
        scm = Git(Process(quiet=True))
        self.clone()
        self.assertEqual(scm.update_sandbox(self.clonedir), 0)

    def testUpdateModifiedSandbox(self):
        scm = Git(Process(quiet=True))
        self.clone()
        self.modify(self.packagedir)
        self.assertEqual(scm.update_sandbox(self.clonedir), 0)

    # TODO: Test more funky changes, conflicts, etc.

    @quiet
    def testBadUpdate(self):
        scm = Git(Process(quiet=True))
        self.clone()
        self.destroy()
        self.assertRaises(SystemExit, scm.update_sandbox, self.clonedir)

    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        # Note: The sandbox is reported as up-to-date
        self.assertEqual(scm.update_sandbox(self.packagedir), 0)

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.update_sandbox, self.packagedir)


class CheckinSandboxTests(GitSetup):

    def testCheckinCleanSandbox(self):
        scm = Git(Process(quiet=True))
        self.assertEqual(scm.checkin_sandbox(self.packagedir, 'testpackage', '2.6', False), 0)

    def testCheckinDirtySandbox(self):
        scm = Git(Process(quiet=True))
        self.modify(self.packagedir)
        self.assertEqual(scm.checkin_sandbox(self.packagedir, 'testpackage', '2.6', False), 0)

    def testCheckinAndPushCleanLocalSandbox(self):
        scm = Git(Process(quiet=True))
        self.assertEqual(scm.checkin_sandbox(self.packagedir, 'testpackage', '2.6', True), 0)

    def testCheckinAndPushDirtyLocalSandbox(self):
        scm = Git(Process(quiet=True))
        self.modify(self.packagedir)
        self.assertEqual(scm.checkin_sandbox(self.packagedir, 'testpackage', '2.6', True), 0)

    def testCheckinAndPushCleanRemoteSandbox(self):
        scm = Git(Process(quiet=True))
        self.clone()
        self.assertEqual(scm.checkin_sandbox(self.clonedir, 'testpackage', '2.6', True), 0)

    def testCheckinAndPushDirtyRemoteSandbox(self):
        scm = Git(Process(quiet=True))
        self.clone()
        self.modify(self.clonedir)
        self.assertEqual(scm.checkin_sandbox(self.clonedir, 'testpackage', '2.6', True), 0)
        self.verify(self.clonedir)
        self.update(self.packagedir)
        self.verify(self.packagedir)

    @quiet
    def testBadPush(self):
        scm = Git(Process(quiet=True))
        self.clone()
        self.destroy()
        self.assertRaises(SystemExit, scm.checkin_sandbox, self.clonedir, 'testpackage', '2.6', True)

    @quiet
    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        self.assertRaises(SystemExit, scm.checkin_sandbox, self.packagedir, 'testpackage', '2.6', False)

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=255))
        self.assertRaises(SystemExit, scm.checkin_sandbox, self.packagedir, 'testpackage', '2.6', False)


class CheckoutUrlTests(GitSetup):

    def testCheckoutUrl(self):
        scm = Git(Process(quiet=True))
        self.assertEqual(scm.checkout_url(self.packagedir, 'testclone'), 0)
        self.assertEqual(isdir('testclone'), True)

    @quiet
    def testBadServer(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        self.assertRaises(SystemExit, scm.checkout_url, self.packagedir, 'testclone')

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.checkout_url, self.packagedir, 'testclone')


class TagExistsTests(GitSetup):

    def testTagDoesNotExist(self):
        scm = Git()
        self.assertEqual(scm.tag_exists(self.packagedir, '2.6'), False)

    def testTagExists(self):
        scm = Git()
        self.tag(self.packagedir, '2.6')
        self.assertEqual(scm.tag_exists(self.packagedir, '2.6'), True)

    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        # Note: The tag is reported as not existing
        self.assertEqual(scm.tag_exists(self.packagedir, '2.6'), False)

    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        # Note: The tag is reported as not existing
        self.assertEqual(scm.tag_exists(self.packagedir, '2.6'), False)

    @quiet
    def testCheckRaises(self):
        scm = Git()
        self.tag(self.packagedir, '2.6')
        self.assertRaises(SystemExit, scm.check_tag_exists, self.packagedir, '2.6')


class CreateTagTests(GitSetup):

    def testCreateTag(self):
        scm = Git()
        self.assertEqual(scm.tag_exists(self.packagedir, '2.6'), False)
        self.assertEqual(scm.create_tag(self.packagedir, '2.6', 'testpackage', '2.6', False), 0)
        self.assertEqual(scm.tag_exists(self.packagedir, '2.6'), True)

    @quiet
    def testCreateExistingTag(self):
        scm = Git(Process(quiet=True))
        self.assertEqual(scm.create_tag(self.packagedir, '2.6', 'testpackage', '2.6', False), 0)
        self.assertEqual(scm.tag_exists(self.packagedir, '2.6'), True)
        self.assertRaises(SystemExit, scm.create_tag, self.packagedir, '2.6', 'testpackage', '2.6', False)

    def testCreateAndPushLocalTag(self):
        scm = Git()
        self.assertEqual(scm.create_tag(self.packagedir, '2.6', 'testpackage', '2.6', True), 0)
        self.assertEqual(scm.tag_exists(self.packagedir, '2.6'), True)

    def testCreateAndPushRemoteTag(self):
        scm = Git(Process(quiet=True))
        self.clone()
        self.assertEqual(scm.create_tag(self.clonedir, '2.6', 'testpackage', '2.6', True), 0)
        self.assertEqual(scm.tag_exists(self.clonedir, '2.6'), True)
        self.assertEqual(scm.tag_exists(self.packagedir, '2.6'), True)

    @quiet
    def testBadPush(self):
        scm = Git(Process(quiet=True))
        self.clone()
        self.destroy()
        self.assertRaises(SystemExit, scm.create_tag, self.packagedir, '2.6', 'testpackage', '2.6', True)

    @quiet
    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        self.assertRaises(SystemExit, scm.create_tag, self.packagedir, '2.6', 'testpackage', '2.6', False)

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.create_tag, self.packagedir, '2.6', 'testpackage', '2.6', False)

