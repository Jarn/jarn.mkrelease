import unittest

from jarn.mkrelease.scm import SCMFactory

from jarn.mkrelease.testing import quiet
from jarn.mkrelease.testing import SubversionSetup
from jarn.mkrelease.testing import MercurialSetup
from jarn.mkrelease.testing import GitSetup


class ValidUrlTests(unittest.TestCase):

    def testSvnUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('svn://'), True)

    def testSvnSshUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('svn+ssh://'), True)

    def testGitUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('git://'), True)

    def testRsyncUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('rsync://'), True)

    def testSshUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('ssh://'), True)

    def testHttpUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('http://'), True)

    def testHttpsUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('https://'), True)

    def testFileUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('file://'), True)

    def testBadProtocol(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('ftp//'), False)

    def testEmptyString(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url(''), False)


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

    def testGetSshByExtension(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_url('ssh://jarn.com/public/foo.git').name, 'git')

    def testGetHttpByHost(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_url('http://hg.jarn.com/public/foo').name, 'hg')

    def testGetHttpByHostWithUser(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_url('http://stefan@hg.jarn.com/public/foo').name, 'hg')

    def testGetHttpsByPath(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_url('https://jarn.com/hg/public/foo').name, 'hg')

    @quiet
    def testGetFile(self):
        # Not unique
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm_from_url, 'file://')

    @quiet
    def testBadUrl(self):
        # Unknown URL scheme
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm_from_url, 'foo://')


class UrlSplitTests(unittest.TestCase):

    def testSplitSvn(self):
        scms = SCMFactory()
        self.assertEqual(scms.urlsplit('svn://jarn.com/public'),
                         ('svn', '', 'jarn.com', '/public', '', ''))

    def testSplitSvnSsh(self):
        scms = SCMFactory()
        self.assertEqual(scms.urlsplit('svn+ssh://stefan@jarn.com/public'),
                         ('svn+ssh', 'stefan', 'jarn.com', '/public', '', ''))

    def testSplitGit(self):
        scms = SCMFactory()
        self.assertEqual(scms.urlsplit('git://jarn.com/public'),
                         ('git', '', 'jarn.com', '/public', '', ''))

    def testSplitRsync(self):
        scms = SCMFactory()
        self.assertEqual(scms.urlsplit('rsync://jarn.com/public'),
                         ('rsync', '', 'jarn.com', '/public', '', ''))

    def testSplitSsh(self):
        scms = SCMFactory()
        self.assertEqual(scms.urlsplit('ssh://stefan@jarn.com//hg/public'),
                         ('ssh', 'stefan', 'jarn.com', '//hg/public', '', ''))

    def testSplitHttp(self):
        scms = SCMFactory()
        self.assertEqual(scms.urlsplit('http://jarn.com/public'),
                         ('http', '', 'jarn.com', '/public', '', ''))

    def testSplitHttps(self):
        scms = SCMFactory()
        self.assertEqual(scms.urlsplit('https://jarn.com/public'),
                         ('https', '', 'jarn.com', '/public', '', ''))

    def testSplitFile(self):
        scms = SCMFactory()
        self.assertEqual(scms.urlsplit('file:///var/dist/public'),
                         ('file', '', '', '/var/dist/public', '', ''))

    def testSplitUnsupported(self):
        scms = SCMFactory()
        self.assertEqual(scms.urlsplit('ftp://jarn.com/public'),
                         ('ftp', '', 'jarn.com', '/public', '', ''))


class IsUrlTests(unittest.TestCase):

    def testSplitSvn(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('svn://jarn.com/public'), True)

    def testSplitSvnSsh(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('svn+ssh://stefan@jarn.com/public'), True)

    def testSplitGit(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('git://jarn.com/public'), True)

    def testSplitRsync(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('rsync://jarn.com/public'), True)

    def testSplitSsh(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('ssh://stefan@jarn.com//hg/public'), True)

    def testSplitHttp(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('http://jarn.com/public'), True)

    def testSplitHttps(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('https://jarn.com/public'), True)

    def testSplitFile(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('file:///var/dist/public'), True)

    def testSplitUnsupported(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('ftp://jarn.com/public'), True)

    def testSplitBadUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url('ssh:'), False)

    def testSplitWhitespace(self):
        scms = SCMFactory()
        self.assertEqual(scms.is_url(' http://'), False)

