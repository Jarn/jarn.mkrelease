import unittest
import os

from os.path import join, isdir

from jarn.mkrelease.scm import Subversion

from jarn.mkrelease.process import Process

from jarn.mkrelease.testing import SubversionSetup
from jarn.mkrelease.testing import MockProcess
from jarn.mkrelease.testing import quiet


class ValidUrlTests(unittest.TestCase):

    def testSvnUrl(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_url('svn://'), True)

    def testSvnSshUrl(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_url('svn+ssh://'), True)

    def testHttpUrl(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_url('http://'), True)

    def testHttpsUrl(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_url('https://'), True)

    def testFileUrl(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_url('file://'), True)

    def testBadProtocol(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_url('git://'), False)

    def testEmptyString(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_url(''), False)

    def testGitSshUrl(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_url('git@github.com:Jarn/jarn.mkrelease'), False)


class ValidSandboxTests(SubversionSetup):

    def testSandbox(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_sandbox(self.clonedir), True)

    def testNotExists(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_sandbox('foo'), False)

    def testNotADir(self):
        scm = Subversion()
        self.assertEqual(scm.is_valid_sandbox(join(self.clonedir, 'setup.py')), False)

    def testNotACheckout(self):
        scm = Subversion()
        self.destroy(self.clonedir)
        self.assertEqual(scm.is_valid_sandbox(self.clonedir), False)

    @quiet
    def testCheckRaises(self):
        scm = Subversion()
        self.assertRaises(SystemExit, scm.check_valid_sandbox, 'foo')
        self.assertRaises(SystemExit, scm.check_valid_sandbox, join(self.clonedir, 'setup.py'))
        self.destroy(self.clonedir)
        self.assertRaises(SystemExit, scm.check_valid_sandbox, self.clonedir)


class RootFromSandboxTests(SubversionSetup):

    def testGetRoot(self):
        scm = Subversion()
        self.assertEqual(scm.get_root_from_sandbox(self.clonedir),
                         self.clonedir)

    def testGetSubfolderRoot(self):
        scm = Subversion()
        self.assertEqual(scm.get_root_from_sandbox(join(self.clonedir, 'testpackage')),
                         self.clonedir)

    @quiet
    def testBadSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.destroy(self.clonedir)
        self.assertRaises(SystemExit, scm.get_root_from_sandbox, self.clonedir)

    @quiet
    def testBadProcess(self):
        scm = Subversion(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.get_root_from_sandbox, self.clonedir)


class BranchFromSandboxTests(SubversionSetup):

    def testGetBranch(self):
        scm = Subversion()
        self.assertEqual(scm.get_branch_from_sandbox(self.clonedir),
            'file://%s/trunk' % self.packagedir)

    def testGetBranchFromSubdir(self):
        scm = Subversion()
        self.assertEqual(scm.get_branch_from_sandbox(join(self.clonedir, 'testpackage')),
            'file://%s/trunk' % self.packagedir)

    def testGetBranchFromBranch(self):
        scm = Subversion()
        branchid = 'file://%s/branches/2.x' % self.packagedir
        self.branch(self.clonedir, branchid)
        self.assertEqual(scm.get_branch_from_sandbox(self.branchdir),
            'file://%s/branches/2.x' % self.packagedir)

    def testGetBranchFromBranchSubdir(self):
        scm = Subversion()
        branchid = 'file://%s/branches/2.x' % self.packagedir
        self.branch(self.clonedir, branchid)
        self.assertEqual(scm.get_branch_from_sandbox(join(self.branchdir, 'testpackage')),
            'file://%s/branches/2.x' % self.packagedir)

    @quiet
    def testBadSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.destroy(self.clonedir)
        self.assertRaises(SystemExit, scm.get_branch_from_sandbox, self.clonedir)

    @quiet
    def testBadProcess(self):
        scm = Subversion(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.get_branch_from_sandbox, self.clonedir)


class UrlFromSandboxTests(SubversionSetup):

    def testGetUrl(self):
        scm = Subversion()
        self.assertEqual(scm.get_url_from_sandbox(self.clonedir),
            'file://%s/trunk' % self.packagedir)

    def testGetAnotherUrl(self):
        scm = Subversion()
        self.assertEqual(scm.get_url_from_sandbox(join(self.clonedir, 'testpackage')),
            'file://%s/trunk/testpackage' % self.packagedir)

    @quiet
    def testBadSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.destroy(self.clonedir)
        self.assertRaises(SystemExit, scm.get_url_from_sandbox, self.clonedir)

    @quiet
    def testBadProcess(self):
        scm = Subversion(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.get_url_from_sandbox, self.clonedir)


class RemoteSandboxTests(SubversionSetup):

    def testIsRemote(self):
        scm = Subversion()
        self.assertEqual(scm.is_remote_sandbox(self.clonedir), True)

    def testIsRemoteSubdir(self):
        scm = Subversion()
        self.assertEqual(scm.is_remote_sandbox(join(self.clonedir, 'testpackage')), True)

    @quiet
    def testBadSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.destroy(self.clonedir)
        self.assertRaises(SystemExit, scm.is_remote_sandbox, self.clonedir)

    @quiet
    def testBadProcess(self):
        scm = Subversion(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.is_remote_sandbox, self.clonedir)


class DirtySandboxTests(SubversionSetup):

    def testCleanSandbox(self):
        scm = Subversion()
        self.assertEqual(scm.is_dirty_sandbox(self.clonedir), False)

    def testModifiedFile(self):
        scm = Subversion()
        self.modify(self.clonedir)
        self.assertEqual(scm.is_dirty_sandbox(self.clonedir), True)

    def testModifiedProp(self):
        scm = Subversion()
        self.modifyprop(self.clonedir)
        self.assertEqual(scm.is_dirty_sandbox(self.clonedir), True)

    def testRemovedFile(self):
        scm = Subversion()
        self.remove(self.clonedir)
        self.assertEqual(scm.is_dirty_sandbox(self.clonedir), True)

    def testDeletedButTrackedFile(self):
        scm = Subversion()
        self.delete(self.clonedir)
        # Note: The sandbox is reported as clean
        self.assertEqual(scm.is_dirty_sandbox(self.clonedir), False)

    def testBadSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.destroy(self.clonedir)
        # Note: The sandbox is reported as *clean*
        self.assertEqual(scm.is_dirty_sandbox(self.clonedir), False)

    @quiet
    def testBadProcess(self):
        scm = Subversion(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.is_dirty_sandbox, self.clonedir)

    @quiet
    def testCheckRaises(self):
        scm = Subversion()
        self.modify(self.clonedir)
        self.assertRaises(SystemExit, scm.check_dirty_sandbox, self.clonedir)


class UncleanSandboxTests(SubversionSetup):

    def testCleanSandbox(self):
        scm = Subversion()
        self.assertEqual(scm.is_unclean_sandbox(self.clonedir), False)

    def testModifiedFile(self):
        scm = Subversion()
        self.modify(self.clonedir)
        self.assertEqual(scm.is_unclean_sandbox(self.clonedir), True)

    def testModifiedProp(self):
        scm = Subversion()
        self.modifyprop(self.clonedir)
        self.assertEqual(scm.is_unclean_sandbox(self.clonedir), True)

    def testRemovedFile(self):
        scm = Subversion()
        self.remove(self.clonedir)
        self.assertEqual(scm.is_unclean_sandbox(self.clonedir), True)

    def testDeletedButTrackedFile(self):
        scm = Subversion()
        self.delete(self.clonedir)
        # Note: The sandbox is reported as unclean
        self.assertEqual(scm.is_unclean_sandbox(self.clonedir), True)

    def testBadSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.destroy(self.clonedir)
        # Note: The sandbox is reported as *clean*
        self.assertEqual(scm.is_unclean_sandbox(self.clonedir), False)

    @quiet
    def testBadProcess(self):
        scm = Subversion(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.is_unclean_sandbox, self.clonedir)

    @quiet
    def testCheckRaises(self):
        scm = Subversion()
        self.modify(self.clonedir)
        self.assertRaises(SystemExit, scm.check_unclean_sandbox, self.clonedir)

    def testTreeConflict(self):
        # Requires Subversion >= 1.6
        def func(cmd):
            if cmd == 'svn --version':
                return 0, ['version 1.6.16']
            else:
                return 0, ['      C foo.py']
                           #      ^ 7th column
        scm = Subversion(MockProcess(func=func))
        self.assertEqual(scm.is_unclean_sandbox(self.clonedir), True)


class CommitSandboxTests(SubversionSetup):

    def testCommitCleanSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.assertEqual(scm.commit_sandbox(self.clonedir, 'testpackage', '2.6', False), 0)

    def testCommitDirtySandbox(self):
        scm = Subversion(Process(quiet=True))
        self.modify(self.clonedir)
        self.assertEqual(scm.commit_sandbox(self.clonedir, 'testpackage', '2.6', False), 0)

    def testCommitAndPushCleanSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.assertEqual(scm.commit_sandbox(self.clonedir, 'testpackage', '2.6', True), 0)

    def testCommitAndPushDirtySandbox(self):
        scm = Subversion(Process(quiet=True))
        self.modify(self.clonedir)
        self.assertEqual(scm.commit_sandbox(self.clonedir, 'testpackage', '2.6', True), 0)
        self.verify(self.clonedir)

    @quiet
    def testBadPush(self):
        scm = Subversion(Process(quiet=True))
        self.modify(self.clonedir)
        self.destroy(self.packagedir)
        self.assertRaises(SystemExit, scm.commit_sandbox, self.clonedir, 'testpackage', '2.6', True)

    @quiet
    def testBadSandbox(self):
        scm = Subversion(Process(quiet=True))
        self.destroy(self.clonedir)
        self.assertRaises(SystemExit, scm.commit_sandbox, self.clonedir, 'testpackage', '2.6', False)

    @quiet
    def testBadProcess(self):
        scm = Subversion(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.commit_sandbox, self.clonedir, 'testpackage', '2.6', False)


class CloneUrlTests(SubversionSetup):

    def testCloneUrl(self):
        scm = Subversion(Process(quiet=True))
        self.assertEqual(scm.clone_url('file://'+self.packagedir, 'testclone2'), 0)
        self.assertEqual(isdir('testclone2'), True)

    @quiet
    def testBadServer(self):
        scm = Subversion(Process(quiet=True))
        self.destroy(self.packagedir)
        self.assertRaises(SystemExit, scm.clone_url, 'file://'+self.packagedir, 'testclone2')

    @quiet
    def testBadProcess(self):
        scm = Subversion(MockProcess(rc=1))
        self.assertRaises(SystemExit, scm.clone_url, 'file://'+self.packagedir, 'testclone2')


class BranchIdTests(SubversionSetup):

    def testMakeBranchId(self):
        scm = Subversion()
        branchid = 'file://%s/branches/2.x' % self.packagedir
        self.assertEqual(scm.make_branchid(self.clonedir, branchid), branchid)

    def testAbsPathBranchId(self):
        scm = Subversion()
        self.dirstack.push(self.packagedir)
        branchid = 'file:branches/2.x'
        self.assertEqual(scm.make_branchid(self.clonedir, branchid),
            'file://%s/branches/2.x' % self.packagedir)

    def testEmptyBranchId(self):
        scm = Subversion()
        self.assertEqual(scm.make_branchid(self.clonedir, ''), '')


class SwitchBranchTests(SubversionSetup):

    @quiet
    def testSwitchBranch(self):
        scm = Subversion(Process(quiet=True))
        trunkid = 'file://%s/trunk' % self.packagedir
        branchid = 'file://%s/branches/2.x' % self.packagedir
        self.branch(self.clonedir, branchid)
        self.assertEqual(scm.get_branch_from_sandbox(self.clonedir), trunkid)
        self.assertEqual(scm.switch_branch(self.clonedir, branchid), 0)
        self.assertEqual(scm.get_branch_from_sandbox(self.clonedir), branchid)

    @quiet
    def testSwitchSameBranch(self):
        scm = Subversion()
        trunkid = 'file://%s/trunk' % self.packagedir
        self.assertEqual(scm.get_branch_from_sandbox(self.clonedir), trunkid)
        self.assertEqual(scm.switch_branch(self.clonedir, trunkid), 0)
        self.assertEqual(scm.get_branch_from_sandbox(self.clonedir), trunkid)

    @quiet
    def testSwitchUnknownBranch(self):
        scm = Subversion(Process(quiet=True))
        branchid = 'file://%s/branches/2.x' % self.packagedir
        self.assertRaises(SystemExit, scm.switch_branch, self.clonedir, branchid)

    @quiet
    def testBadSandbox(self):
        scm = Subversion(Process(quiet=True))
        branchid = 'file://%s/branches/2.x' % self.packagedir
        self.destroy(self.clonedir)
        self.assertRaises(SystemExit, scm.switch_branch, self.clonedir, branchid)

    @quiet
    def testBadProcess(self):
        scm = Subversion(MockProcess(rc=1))
        branchid = 'file://%s/branches/2.x' % self.packagedir
        self.assertRaises(SystemExit, scm.switch_branch, self.clonedir, branchid)


class TagExistsTests(SubversionSetup):

    def testTagDoesNotExist(self):
        scm = Subversion()
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.assertEqual(scm.tag_exists(self.clonedir, tagid), False)

    def testTagExists(self):
        scm = Subversion()
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.tag(self.clonedir, tagid)
        self.assertEqual(scm.tag_exists(self.clonedir, tagid), True)

    @quiet
    def testBadRepository(self):
        scm = Subversion(Process(quiet=True))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.destroy(self.packagedir)
        self.assertRaises(SystemExit, scm.check_tag_exists, self.clonedir, tagid)

    @quiet
    def testBadProcess(self):
        scm = Subversion(MockProcess(rc=1))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.assertRaises(SystemExit, scm.check_tag_exists, self.clonedir, tagid)

    @quiet
    def testCheckRaises(self):
        scm = Subversion()
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.tag(self.clonedir, tagid)
        self.assertRaises(SystemExit, scm.check_tag_exists, self.clonedir, tagid)


class TagIdTests(SubversionSetup):

    def testTagIdFromTrunk(self):
        scm = Subversion()
        self.assertEqual(scm.make_tagid(self.clonedir, '2.6'),
            'file://%s/tags/2.6' % self.packagedir)

    def testTagIdFromBranch(self):
        scm = Subversion()
        branchid = 'file://%s/branches/2.x' % self.packagedir
        self.branch(self.clonedir, branchid)
        self.assertEqual(scm.get_branch_from_sandbox(self.branchdir),
            'file://%s/branches/2.x' % self.packagedir)
        self.assertEqual(scm.make_tagid(self.branchdir, '2.6'),
            'file://%s/tags/2.6' % self.packagedir)

    def testTagIdFromTag(self):
        scm = Subversion()
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.tag(self.clonedir, tagid)
        self.assertEqual(scm.tag_exists(self.tagdir, tagid), True)
        self.assertEqual(scm.make_tagid(self.tagdir, '2.7'),
            'file://%s/tags/2.7' % self.packagedir)

    @quiet
    def testTagIdFromBadUrl(self):
        scm = Subversion(MockProcess(rc=0, lines=['', 'URL: file://svn/testpackage']))
        self.assertRaises(SystemExit, scm.make_tagid, self.clonedir, '2.6')


class CodespeakTagIdTests(SubversionSetup):

    def setUp(self):
        SubversionSetup.setUp(self)
        process = Process(quiet=True)
        process.popen('svn mv -m"Rename" "file://%s/tags" "file://%s/tag"' %
            (self.packagedir, self.packagedir))
        process.popen('svn mv -m"Rename" "file://%s/branches" "file://%s/branch"' %
            (self.packagedir, self.packagedir))

    def testTagIdFromTrunk(self):
        scm = Subversion()
        self.assertEqual(scm.make_tagid(self.clonedir, '2.6'),
            'file://%s/tag/2.6' % self.packagedir)

    def testTagIdFromBranch(self):
        scm = Subversion()
        branchid = 'file://%s/branch/2.x' % self.packagedir
        self.branch(self.clonedir, branchid)
        self.assertEqual(scm.get_branch_from_sandbox(self.branchdir),
            'file://%s/branch/2.x' % self.packagedir)
        self.assertEqual(scm.make_tagid(self.branchdir, '2.6'),
            'file://%s/tag/2.6' % self.packagedir)

    def testTagIdFromTag(self):
        scm = Subversion()
        tagid = 'file://%s/tag/2.6' % self.packagedir
        self.tag(self.clonedir, tagid)
        self.assertEqual(scm.tag_exists(self.tagdir, tagid), True)
        self.assertEqual(scm.make_tagid(self.tagdir, '2.7'),
            'file://%s/tag/2.7' % self.packagedir)

    @quiet
    def testTagIdFromBadUrl(self):
        scm = Subversion(MockProcess(rc=0, lines=['', 'URL: file://svn/testpackage']))
        self.assertRaises(SystemExit, scm.make_tagid, self.clonedir, '2.6')


class CreateTagTests(SubversionSetup):

    def testCreateTag(self):
        scm = Subversion(Process(quiet=True))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.assertEqual(scm.tag_exists(self.clonedir, tagid), False)
        self.assertEqual(scm.create_tag(self.clonedir, tagid, 'testpackage', '2.6', False), 0)
        self.assertEqual(scm.tag_exists(self.clonedir, tagid), True)

    @quiet
    def testCreateExistingTag(self):
        scm = Subversion(Process(quiet=True))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.assertEqual(scm.create_tag(self.clonedir, tagid, 'testpackage', '2.6', False), 0)
        self.assertEqual(scm.tag_exists(self.clonedir, tagid), True)
        # Note: This works! Subversion just copies stuff into a subdirectory...
        self.assertEqual(scm.create_tag(self.clonedir, tagid, 'testpackage', '2.6', False), 0)
        # Note: Only on the third attempt tagging fails
        self.assertRaises(SystemExit, scm.create_tag, self.clonedir, tagid, 'testpackage', '2.6', False)

    def testCreateAndPushTag(self):
        scm = Subversion(Process(quiet=True))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.assertEqual(scm.create_tag(self.clonedir, tagid, 'testpackage', '2.6', True), 0)
        self.assertEqual(scm.tag_exists(self.clonedir, tagid), True)
        #self.assertEqual(scm.tag_exists(self.packagedir, tagid), True)

    @quiet
    def testBadPush(self):
        scm = Subversion(Process(quiet=True))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.destroy(self.packagedir)
        self.assertRaises(SystemExit, scm.create_tag, self.clonedir, tagid, 'testpackage', '2.6', True)

    @quiet
    def testBadSandbox(self):
        scm = Subversion(Process(quiet=True))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.destroy(self.clonedir)
        self.assertRaises(SystemExit, scm.create_tag, self.clonedir, tagid, 'testpackage', '2.6', False)

    @quiet
    def testBadProcess(self):
        scm = Subversion(MockProcess(rc=1))
        tagid = 'file://%s/tags/2.6' % self.packagedir
        self.assertRaises(SystemExit, scm.create_tag, self.clonedir, tagid, 'testpackage', '2.6', False)


class GetVersionTests(unittest.TestCase):

    def testGetVersion(self):
        scm = Subversion()
        self.assertNotEqual(scm.get_version(), '')

    def testVersionInfo(self):
        scm = Subversion()
        self.assertNotEqual(scm.version_info, ())

