import unittest

from jarn.mkrelease.scm import SCMContainer

from jarn.mkrelease.testing import quiet
from jarn.mkrelease.testing import SubversionSetup
from jarn.mkrelease.testing import MercurialSetup
from jarn.mkrelease.testing import GitSetup


class ValidUrlTests(unittest.TestCase):

    def testSvnUrl(self):
        scms = SCMContainer()
        self.assertEqual(scms.is_valid_url('svn://'), True)

    def testSvnSshUrl(self):
        scms = SCMContainer()
        self.assertEqual(scms.is_valid_url('svn+ssh://'), True)

    def testGitUrl(self):
        scms = SCMContainer()
        self.assertEqual(scms.is_valid_url('git://'), True)

    def testRsyncUrl(self):
        scms = SCMContainer()
        self.assertEqual(scms.is_valid_url('rsync://'), True)

    def testSshUrl(self):
        scms = SCMContainer()
        self.assertEqual(scms.is_valid_url('ssh://'), True)

    def testHttpUrl(self):
        scms = SCMContainer()
        self.assertEqual(scms.is_valid_url('http://'), True)

    def testHttpsUrl(self):
        scms = SCMContainer()
        self.assertEqual(scms.is_valid_url('https://'), True)

    def testFileUrl(self):
        scms = SCMContainer()
        self.assertEqual(scms.is_valid_url('file://'), True)

    def testBadProtocol(self):
        scms = SCMContainer()
        self.assertEqual(scms.is_valid_url('ftp://'), False)

    def testEmptyString(self):
        scms = SCMContainer()
        self.assertEqual(scms.is_valid_url(''), False)


class ScmFromTypeTests(unittest.TestCase):

    def testGetSubversion(self):
        scms = SCMContainer()
        self.assertEqual(scms.get_scm_from_type('svn').name, 'svn')

    def testGetMercurial(self):
        scms = SCMContainer()
        self.assertEqual(scms.get_scm_from_type('hg').name, 'hg')

    def testGetGit(self):
        scms = SCMContainer()
        self.assertEqual(scms.get_scm_from_type('git').name, 'git')

    @quiet
    def testBadSCM(self):
        scms = SCMContainer()
        self.assertRaises(SystemExit, scms.get_scm_from_type, 'foo')


class SubversionFromSandboxTests(SubversionSetup):

    def testGetSubversion(self):
        scms = SCMContainer()
        self.assertEqual(scms.get_scm_from_sandbox(self.clonedir).name, 'svn')

    @quiet
    def testBadSandbox(self):
        scms = SCMContainer()
        self.destroy(self.clonedir)
        self.assertRaises(SystemExit, scms.get_scm_from_sandbox, self.clonedir)

    @quiet
    def testNoSuchFile(self):
        scms = SCMContainer()
        self.assertRaises(SystemExit, scms.get_scm_from_sandbox, 'foobarbaz.peng')


class MercurialFromSandboxTests(MercurialSetup):

    def testGetMercurial(self):
        scms = SCMContainer()
        self.destroy(name='svn')
        self.assertEqual(scms.get_scm_from_sandbox(self.packagedir).name, 'hg')

    @quiet
    def testAmbiguousSandbox(self):
        scms = SCMContainer()
        self.assertRaises(SystemExit, scms.get_scm_from_sandbox, self.packagedir)


class GitFromSandboxTests(GitSetup):

    def testGetGit(self):
        scms = SCMContainer()
        self.destroy(name='svn')
        self.assertEqual(scms.get_scm_from_sandbox(self.packagedir).name, 'git')

    @quiet
    def testAmbiguousSandbox(self):
        scms = SCMContainer()
        self.assertRaises(SystemExit, scms.get_scm_from_sandbox, self.packagedir)


class ScmFromUrlTests(unittest.TestCase):

    def testGetSvn(self):
        scms = SCMContainer()
        self.assertEqual(scms.get_scm_from_url('svn://').name, 'svn')

    def testGetSvnSsh(self):
        scms = SCMContainer()
        self.assertEqual(scms.get_scm_from_url('svn+ssh://').name, 'svn')

    def testGetGit(self):
        scms = SCMContainer()
        self.assertEqual(scms.get_scm_from_url('git://').name, 'git')

    def testGetRsync(self):
        scms = SCMContainer()
        self.assertEqual(scms.get_scm_from_url('rsync://').name, 'git')

    @quiet
    def testGetHttp(self):
        scms = SCMContainer()
        self.assertRaises(SystemExit, scms.get_scm_from_url, 'http://')

    @quiet
    def testGetHttps(self):
        scms = SCMContainer()
        self.assertRaises(SystemExit, scms.get_scm_from_url, 'https://')

    @quiet
    def testGetFile(self):
        scms = SCMContainer()
        self.assertRaises(SystemExit, scms.get_scm_from_url, 'file://')

    @quiet
    def testBadUrl(self):
        scms = SCMContainer()
        self.assertRaises(SystemExit, scms.get_scm_from_url, 'foo://')

