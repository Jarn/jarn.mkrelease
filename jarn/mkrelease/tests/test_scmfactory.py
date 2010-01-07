import unittest

from jarn.mkrelease.scm import SCMFactory

from jarn.mkrelease.testing import quiet
from jarn.mkrelease.testing import SubversionSetup
from jarn.mkrelease.testing import MercurialSetup
from jarn.mkrelease.testing import GitSetup


class ValidUrlTests(unittest.TestCase):

    def testSvnUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_valid_url('svn://'), True)

    def testSvnSshUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_valid_url('svn+ssh://'), True)

    def testGitUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_valid_url('git://'), True)

    def testRsyncUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_valid_url('rsync://'), True)

    def testSshUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_valid_url('ssh://'), True)

    def testHttpUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_valid_url('http://'), True)

    def testHttpsUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_valid_url('https://'), True)

    def testFileUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_valid_url('file://'), True)

    def testBadProtocol(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_valid_url('ftp://'), False)

    def testEmptyString(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_valid_url(''), False)


class ScmFromTypeTests(unittest.TestCase):

    def testGetSubversion(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_type('svn').name, 'svn')

    def testGetMercurial(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_type('hg').name, 'hg')

    def testGetGit(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_type('git').name, 'git')

    @quiet
    def testBadSCM(self):
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm_from_type, 'foo')


class SubversionFromSandboxTests(SubversionSetup):

    def testGetSubversion(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_sandbox(self.clonedir).name, 'svn')

    @quiet
    def testBadSandbox(self):
        scms = SCMFactory()
        self.destroy(self.clonedir)
        self.assertRaises(SystemExit, scms.get_scm_from_sandbox, self.clonedir)

    @quiet
    def testNoSuchFile(self):
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm_from_sandbox, 'foobarbaz.peng')


class MercurialFromSandboxTests(MercurialSetup):

    def testGetMercurial(self):
        scms = SCMFactory()
        self.destroy(name='svn')
        self.assertEqual(scms.get_scm_from_sandbox(self.packagedir).name, 'hg')

    @quiet
    def testAmbiguousSandbox(self):
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm_from_sandbox, self.packagedir)


class GitFromSandboxTests(GitSetup):

    def testGetGit(self):
        scms = SCMFactory()
        self.destroy(name='svn')
        self.assertEqual(scms.get_scm_from_sandbox(self.packagedir).name, 'git')

    @quiet
    def testAmbiguousSandbox(self):
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm_from_sandbox, self.packagedir)


class ScmFromUrlTests(unittest.TestCase):

    def testGetSvn(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_url('svn://').name, 'svn')

    def testGetSvnSsh(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_url('svn+ssh://').name, 'svn')

    def testGetGit(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_url('git://').name, 'git')

    def testGetRsync(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_url('rsync://').name, 'git')

    @quiet
    def testGetHttp(self):
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm_from_url, 'http://')

    @quiet
    def testGetHttps(self):
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm_from_url, 'https://')

    @quiet
    def testGetFile(self):
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm_from_url, 'file://')

    @quiet
    def testBadUrl(self):
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm_from_url, 'foo://')

