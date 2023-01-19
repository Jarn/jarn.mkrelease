import unittest

from jarn.mkrelease.process import Process
from jarn.mkrelease.scm import SCMFactory

from jarn.mkrelease.testing import quiet
from jarn.mkrelease.testing import SubversionSetup
from jarn.mkrelease.testing import MercurialSetup
from jarn.mkrelease.testing import GitSetup


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

    def testGetFile(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_url('file:///var/dist/public/foo.git').name, 'git')

    def testGetRelativeFile(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_url('file:var/dist/public/foo.git').name, 'git')

    def testGetSshGitHub(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_url('ssh://git@github.com/jondoe/foo').name, 'git')

    def testGetHttpGitHub(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_url('http://github.com/jondoe/foo').name, 'git')

    def testGetHttpsGitHub(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_url('https://jondoe@github.com/jondoe/foo').name, 'git')

    @quiet
    def testNotUnique(self):
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm_from_url, 'http://')

    @quiet
    def testBadUrl(self):
        # Unknown URL scheme
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm_from_url, 'foo://')


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

    @quiet
    def testAmbiguousSandbox(self):
        scms = SCMFactory()
        process = Process()
        self.dirstack.push(self.clonedir)
        process.popen('git init .')
        process.popen('git add README.txt setup.py testpackage/__init__.py')
        process.popen('git commit -m"Import"')
        self.dirstack.pop()
        self.assertRaises(SystemExit, scms.get_scm_from_sandbox, self.clonedir)


class MercurialFromSandboxTests(MercurialSetup):

    def testGetMercurial(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_sandbox(self.packagedir).name, 'hg')

    @quiet
    def testAmbiguousSandbox(self):
        scms = SCMFactory()
        process = Process()
        self.dirstack.push(self.packagedir)
        process.popen('git init .')
        process.popen('git add README.txt setup.py testpackage/__init__.py')
        process.popen('git commit -m"Import"')
        self.dirstack.pop()
        self.assertRaises(SystemExit, scms.get_scm_from_sandbox, self.packagedir)


class GitFromSandboxTests(GitSetup):

    def testGetGit(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm_from_sandbox(self.packagedir).name, 'git')

    @quiet
    def testAmbiguousSandbox(self):
        scms = SCMFactory()
        process = Process()
        self.dirstack.push(self.packagedir)
        process.popen('hg init .')
        process.popen('hg add README.txt setup.py testpackage/__init__.py')
        process.popen('hg commit -m"Import"')
        self.dirstack.pop()
        self.assertRaises(SystemExit, scms.get_scm_from_sandbox, self.packagedir)


class SubversionGetScmTests(SubversionSetup):

    def testGetFromType(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm('svn', self.clonedir).name, 'svn')

    def testGetFromUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm(None, 'svn://jarn.com/public').name, 'svn')

    def testGetFromFileUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm(None, 'file://'+self.packagedir).name, 'svn')

    @quiet
    def testNonRepo(self):
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm, None, 'file://'+self.clonedir)

    def testGetFromSandbox(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm(None, self.clonedir).name, 'svn')

    @quiet
    def testBadSandbox(self):
        scms = SCMFactory()
        self.destroy(self.clonedir)
        self.assertRaises(SystemExit, scms.get_scm, None, self.clonedir)

    @quiet
    def testNoSuchFile(self):
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm, None, 'foobarbaz.peng')

    @quiet
    def testAmbiguousSandbox(self):
        scms = SCMFactory()
        process = Process()
        self.dirstack.push(self.clonedir)
        process.popen('git init .')
        process.popen('git add README.txt setup.py testpackage/__init__.py')
        process.popen('git commit -m"Import"')
        self.dirstack.pop()
        self.assertRaises(SystemExit, scms.get_scm, None, self.clonedir)


class MercurialGetScmTests(MercurialSetup):

    def testGetFromType(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm('hg', self.packagedir).name, 'hg')

    def testGetFromUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm(None, 'ssh://jarn.com/hg/public').name, 'hg')

    def testGetFromFileUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm(None, 'file://'+self.packagedir).name, 'hg')

    @quiet
    def testNonTopLevel(self):
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm, None, 'file://'+self.packagedir+'/testpackage')

    def testGetFromSandbox(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm(None, self.packagedir).name, 'hg')

    @quiet
    def testAmbiguousSandbox(self):
        scms = SCMFactory()
        process = Process()
        self.dirstack.push(self.packagedir)
        process.popen('git init .')
        process.popen('git add README.txt setup.py testpackage/__init__.py')
        process.popen('git commit -m"Import"')
        self.dirstack.pop()
        self.assertRaises(SystemExit, scms.get_scm, None, self.packagedir)

    @quiet
    def testBadSandbox(self):
        scms = SCMFactory()
        self.destroy()
        self.assertRaises(SystemExit, scms.get_scm, None, self.packagedir)


class GitGetScmTests(GitSetup):

    def testGetFromType(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm('git', self.packagedir).name, 'git')

    def testGetFromUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm(None, 'git://jarn.com/public').name, 'git')

    def testGetFromFileUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm(None, 'file://'+self.packagedir).name, 'git')

    @quiet
    def testNonTopLevel(self):
        scms = SCMFactory()
        self.assertRaises(SystemExit, scms.get_scm, None, 'file://'+self.packagedir+'/testpackage')

    def testGetFromSshUrl(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm(None, 'git@github.com:Jarn/jarn.mkrelease').name, 'git')

    def testGetFromSandbox(self):
        scms = SCMFactory()
        self.assertEqual(scms.get_scm(None, self.packagedir).name, 'git')

    @quiet
    def testAmbiguousSandbox(self):
        scms = SCMFactory()
        process = Process()
        self.dirstack.push(self.packagedir)
        process.popen('hg init .')
        process.popen('hg add README.txt setup.py testpackage/__init__.py')
        process.popen('hg commit -m"Import"')
        self.dirstack.pop()
        self.assertRaises(SystemExit, scms.get_scm, None, self.packagedir)

    @quiet
    def testBadSandbox(self):
        scms = SCMFactory()
        self.destroy()
        self.assertRaises(SystemExit, scms.get_scm, None, self.packagedir)

