import unittest

from jarn.mkrelease.scm import SCMFactory
from jarn.mkrelease.urlparser import URLParser

from jarn.mkrelease.testing import quiet
from jarn.mkrelease.testing import SubversionSetup
from jarn.mkrelease.testing import MercurialSetup
from jarn.mkrelease.testing import GitSetup


class ValidUrlTests(unittest.TestCase):

    def testSvnUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('svn://'), True)

    def testSvnSshUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('svn+ssh://'), True)

    def testGitUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('git://'), True)

    def testRsyncUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('rsync://'), True)

    def testSshUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('ssh://'), True)

    def testHttpUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('http://'), True)

    def testHttpsUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('https://'), True)

    def testFileUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('file://'), True)

    def testBadProtocol(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('ftp//'), False)

    def testEmptyString(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url(''), False)


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
        urlparser = URLParser()
        self.assertEqual(urlparser.split('svn://jarn.com/public'),
                         ('svn', '', 'jarn.com', '/public', '', ''))

    def testSplitSvnSsh(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.split('svn+ssh://stefan@jarn.com/public'),
                         ('svn+ssh', 'stefan', 'jarn.com', '/public', '', ''))

    def testSplitGit(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.split('git://jarn.com/public'),
                         ('git', '', 'jarn.com', '/public', '', ''))

    def testSplitRsync(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.split('rsync://jarn.com/public'),
                         ('rsync', '', 'jarn.com', '/public', '', ''))

    def testSplitSsh(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.split('ssh://stefan@jarn.com//hg/public'),
                         ('ssh', 'stefan', 'jarn.com', '//hg/public', '', ''))

    def testSplitHttp(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.split('http://jarn.com/public'),
                         ('http', '', 'jarn.com', '/public', '', ''))

    def testSplitHttps(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.split('https://jarn.com/public'),
                         ('https', '', 'jarn.com', '/public', '', ''))

    def testSplitFile(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.split('file:///var/dist/public'),
                         ('file', '', '', '/var/dist/public', '', ''))

    def testSplitUnsupported(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.split('ftp://jarn.com/public'),
                         ('ftp', '', 'jarn.com', '/public', '', ''))

    def testSplitBadUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.split('ssh:stefan@jarn.com/public'),
                         ('', '', '', 'ssh:stefan@jarn.com/public', '', ''))


class IsUrlTests(unittest.TestCase):

    def testSvn(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('svn://jarn.com/public'), True)

    def testSvnSsh(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('svn+ssh://stefan@jarn.com/public'), True)

    def testGit(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('git://jarn.com/public'), True)

    def testRsync(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('rsync://jarn.com/public'), True)

    def testSsh(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('ssh://stefan@jarn.com//hg/public'), True)

    def testHttp(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('http://jarn.com/public'), True)

    def testHttps(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('https://jarn.com/public'), True)

    def testFile(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('file:///var/dist/public'), True)

    def testUnsupported(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('ftp://jarn.com/public'), True)

    def testBadUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('ssh:'), False)

    def testWhitespace(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url(' http://'), False)

