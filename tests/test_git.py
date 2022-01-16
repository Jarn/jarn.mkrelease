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

    def testGitSshUrl(self):
        scm = Git()
        self.assertEqual(scm.is_valid_url('git@github.com:Jarn/jarn.mkrelease'), True)


class ValidSandboxTests(GitSetup):

    def testSandbox(self):
        scm = Git()
        self.assertEqual(scm.is_valid_sandbox(self.packagedir), True)

    def testSubdirOfSandbox(self):
        scm = Git()
        self.assertEqual(scm.is_valid_sandbox(join(self.packagedir, 'testpackage')), True)

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


class RootFromSandboxTests(GitSetup):

    def testGetRoot(self):
        scm = Git()
        self.assertEqual(scm.get_root_from_sandbox(self.packagedir),
                         self.packagedir)

    def testGetSubfolderRoot(self):
        scm = Git()
        self.assertEqual(scm.get_root_from_sandbox(join(self.packagedir, 'testpackage')),
                         self.packagedir)

    def testGetCloneRoot(self):
        scm = Git()
        self.clone()
        self.assertEqual(scm.get_root_from_sandbox(self.clonedir),
                         self.clonedir)

    def testGetCloneSubfolderRoot(self):
        scm = Git()
        self.clone()
        self.assertEqual(scm.get_root_from_sandbox(join(self.clonedir, 'testpackage')),
                         self.clonedir)

    @quiet
    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        self.assertRaises(SystemExit, scm.get_root_from_sandbox, self.packagedir)

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.get_root_from_sandbox, self.packagedir)


class BranchFromSandboxTests(GitSetup):

    def testGetLocalBranch(self):
        scm = Git()
        self.assertEqual(scm.get_branch_from_sandbox(self.packagedir), 'master')

    def testGetLocalBranchFromBranch(self):
        scm = Git()
        self.branch(self.packagedir, '2.x')
        self.assertEqual(scm.get_branch_from_sandbox(self.packagedir), '2.x')

    def testGetRemoteBranch(self):
        scm = Git()
        self.clone()
        self.assertEqual(scm.get_branch_from_sandbox(self.clonedir), 'master')

    @quiet
    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        self.assertRaises(SystemExit, scm.get_branch_from_sandbox, self.packagedir)

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.get_branch_from_sandbox, self.packagedir)


class RemoteFromSandboxTests(GitSetup):

    def testGetLocal(self):
        scm = Git()
        self.assertEqual(scm.get_remote_from_sandbox(self.packagedir), '')

    def testGetRemote(self):
        scm = Git()
        self.clone()
        self.assertEqual(scm.get_remote_from_sandbox(self.clonedir), 'origin')

    @quiet
    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        self.assertRaises(SystemExit, scm.get_remote_from_sandbox, self.packagedir)

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.get_remote_from_sandbox, self.packagedir)

    @quiet
    def testWhitebox(self):
        def func(cmd):
            if cmd == 'git branch':
                return 0, ['* master']
            return 1, []

        scm = Git(MockProcess(func=func))
        self.assertRaises(SystemExit, scm.get_remote_from_sandbox, self.packagedir)


class TrackedBranchFromSandboxTests(GitSetup):

    def testGetLocal(self):
        scm = Git()
        self.assertEqual(scm.get_tracked_branch_from_sandbox(self.packagedir), '')

    def testGetRemote(self):
        scm = Git()
        self.clone()
        self.assertEqual(scm.get_tracked_branch_from_sandbox(self.clonedir), 'master')

    @quiet
    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        self.assertRaises(SystemExit, scm.get_tracked_branch_from_sandbox, self.packagedir)

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.get_tracked_branch_from_sandbox, self.packagedir)

    @quiet
    def testWhitebox(self):
        def func(cmd):
            if cmd == 'git branch':
                return 0, ['* master']
            return 1, []

        scm = Git(MockProcess(func=func))
        self.assertRaises(SystemExit, scm.get_tracked_branch_from_sandbox, self.packagedir)


class UrlFromSandboxTests(GitSetup):

    def testGetLocalUrl(self):
        scm = Git()
        self.assertEqual(scm.get_url_from_sandbox(self.packagedir), '')

    def testGetRemoteUrl(self):
        scm = Git()
        self.clone()
        self.assertEqual(scm.get_url_from_sandbox(self.clonedir), self.packagedir)

    @quiet
    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        self.assertRaises(SystemExit, scm.get_url_from_sandbox, self.packagedir)

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.get_url_from_sandbox, self.packagedir)

    @quiet
    def testWhitebox(self):
        self.called = 0

        def func(cmd):
            if cmd == 'git branch':
                return 0, ['* master']
            if cmd == 'git config -l':
                self.called += 1
                if self.called == 1:
                    return 0, ['branch.master.remote=origin']
            return 1, []

        scm = Git(MockProcess(func=func))
        self.assertRaises(SystemExit, scm.get_url_from_sandbox, self.packagedir)


class RemoteSandboxTests(GitSetup):

    def testIsLocal(self):
        scm = Git()
        self.assertEqual(scm.is_remote_sandbox(self.packagedir), False)

    def testIsRemote(self):
        scm = Git()
        self.clone()
        self.assertEqual(scm.is_remote_sandbox(self.clonedir), True)

    @quiet
    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        self.assertRaises(SystemExit, scm.is_remote_sandbox, self.packagedir)

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

    @quiet
    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        self.assertRaises(SystemExit, scm.is_dirty_sandbox, self.packagedir)

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=128))
        self.assertRaises(SystemExit, scm.is_dirty_sandbox, self.packagedir)

    @quiet
    def testCheckRaises(self):
        scm = Git()
        self.modify(self.packagedir)
        self.assertRaises(SystemExit, scm.check_dirty_sandbox, self.packagedir)


class UncleanSandboxTests(GitSetup):

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
        # Note: The sandbox is reported as unclean
        self.assertEqual(scm.is_unclean_sandbox(self.packagedir), True)

    @quiet
    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        self.assertRaises(SystemExit, scm.is_unclean_sandbox, self.packagedir)

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=128))
        self.assertRaises(SystemExit, scm.is_unclean_sandbox, self.packagedir)

    @quiet
    def testCheckRaises(self):
        scm = Git()
        self.modify(self.packagedir)
        self.assertRaises(SystemExit, scm.check_unclean_sandbox, self.packagedir)


class CommitSandboxTests(GitSetup):

    def testCommitCleanSandbox(self):
        scm = Git(Process(quiet=True))
        self.assertEqual(scm.commit_sandbox(self.packagedir, 'testpackage', '2.6', False), 0)

    def testCommitDirtySandbox(self):
        scm = Git(Process(quiet=True))
        self.modify(self.packagedir)
        self.assertEqual(scm.commit_sandbox(self.packagedir, 'testpackage', '2.6', False), 0)

    @quiet
    def testCommitAndPushCleanLocalSandbox(self):
        scm = Git(Process(quiet=True))
        self.assertEqual(scm.commit_sandbox(self.packagedir, 'testpackage', '2.6', True), 0)

    @quiet
    def testCommitAndPushDirtyLocalSandbox(self):
        scm = Git(Process(quiet=True))
        self.modify(self.packagedir)
        self.assertEqual(scm.commit_sandbox(self.packagedir, 'testpackage', '2.6', True), 0)

    def testCommitAndPushCleanRemoteSandbox(self):
        scm = Git(Process(quiet=True))
        self.clone()
        self.assertEqual(scm.commit_sandbox(self.clonedir, 'testpackage', '2.6', True), 0)

    def testCommitAndPushDirtyRemoteSandbox(self):
        scm = Git(Process(quiet=True))
        self.clone()
        self.modify(self.clonedir)
        self.assertEqual(scm.commit_sandbox(self.clonedir, 'testpackage', '2.6', True), 0)
        self.verify(self.clonedir)
        self.update(self.packagedir)
        self.verify(self.packagedir)

    @quiet
    def testBadPush(self):
        scm = Git(Process(quiet=True))
        self.clone()
        self.destroy()
        self.assertRaises(SystemExit, scm.commit_sandbox, self.clonedir, 'testpackage', '2.6', True)

    @quiet
    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        self.assertRaises(SystemExit, scm.commit_sandbox, self.packagedir, 'testpackage', '2.6', False)

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=255))
        self.assertRaises(SystemExit, scm.commit_sandbox, self.packagedir, 'testpackage', '2.6', False)


class CloneUrlTests(GitSetup):

    def testCloneUrl(self):
        scm = Git(Process(quiet=True))
        self.assertEqual(scm.clone_url(self.packagedir, 'testclone'), 0)
        self.assertEqual(isdir('testclone'), True)

    @quiet
    def testBadServer(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        self.assertRaises(SystemExit, scm.clone_url, self.packagedir, 'testclone')

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.clone_url, self.packagedir, 'testclone')


class BranchIdTests(GitSetup):

    def testMakeBranchId(self):
        scm = Git()
        self.assertEqual(scm.make_branchid(self.packagedir, '2.x'), '2.x')

    def testEmptyBranchId(self):
        scm = Git()
        self.assertEqual(scm.make_branchid(self.packagedir, ''), 'master')


class SwitchBranchTests(GitSetup):

    @quiet
    def testSwitchBranch(self):
        scm = Git(Process(quiet=True))
        self.branch(self.packagedir, '2.x')
        self.assertEqual(scm.get_branch_from_sandbox(self.packagedir), '2.x')
        self.assertEqual(scm.switch_branch(self.packagedir, 'master'), 0)
        self.assertEqual(scm.get_branch_from_sandbox(self.packagedir), 'master')

    @quiet
    def testSwitchSameBranch(self):
        scm = Git()
        self.assertEqual(scm.get_branch_from_sandbox(self.packagedir), 'master')
        self.assertEqual(scm.switch_branch(self.packagedir, 'master'), 0)
        self.assertEqual(scm.get_branch_from_sandbox(self.packagedir), 'master')

    @quiet
    def testSwitchRemoteBranch(self):
        scm = Git(Process(quiet=True))
        self.branch(self.packagedir, '2.x')
        self.clone()
        self.assertEqual(scm.get_branch_from_sandbox(self.clonedir), 'master')
        self.assertEqual(scm.switch_branch(self.clonedir, '2.x'), 0)
        self.assertEqual(scm.get_branch_from_sandbox(self.clonedir), '2.x')

    @quiet
    def testSwitchUnknownBranch(self):
        scm = Git(Process(quiet=True))
        self.assertRaises(SystemExit, scm.switch_branch, self.packagedir, '2.x')

    @quiet
    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        self.assertRaises(SystemExit, scm.switch_branch, self.packagedir, 'master')

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.switch_branch, self.packagedir, 'master')


class TagExistsTests(GitSetup):

    def testTagDoesNotExist(self):
        scm = Git()
        self.assertEqual(scm.tag_exists(self.packagedir, '2.6'), False)

    def testTagExists(self):
        scm = Git()
        self.tag(self.packagedir, '2.6')
        self.assertEqual(scm.tag_exists(self.packagedir, '2.6'), True)

    @quiet
    def testBadSandbox(self):
        scm = Git(Process(quiet=True))
        self.destroy()
        self.assertRaises(SystemExit, scm.check_tag_exists, self.packagedir, '2.6')

    @quiet
    def testBadProcess(self):
        scm = Git(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.check_tag_exists, self.packagedir, '2.6')

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

    @quiet
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


class GetVersionTests(unittest.TestCase):

    def testGetVersion(self):
        scm = Git()
        self.assertNotEqual(scm.get_version(), '')

    def testVersionInfo(self):
        scm = Git()
        self.assertNotEqual(scm.version_info, ())

