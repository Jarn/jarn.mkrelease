import sys
import os
import zipfile
import pkg_resources

from os.path import join

from jarn.mkrelease.setuptools import Setuptools
from jarn.mkrelease.process import Process

from jarn.mkrelease.testing import SubversionSetup
from jarn.mkrelease.testing import MercurialSetup
from jarn.mkrelease.testing import GitSetup


class defaults:
    python = sys.executable


def contains(archive, name):
    for info in zipfile.ZipFile(archive).infolist():
        if name in info.filename:
            return True
    return False


def get_finder(type):
    for ep in pkg_resources.iter_entry_points('setuptools.file_finders'):
        if type.lower() in ep.name:
            return ep.load()


class SubversionTests(SubversionSetup):

    def testSubversionFinder(self):
        files = list(get_finder('svn')(self.clonedir))
        self.failUnless(join(self.clonedir, 'testpackage', 'subversion_only.py') in files)
        self.failUnless(join(self.clonedir, 'testpackage', 'subversion_only.txt') in files)

    def testSubversionFinderNoDirname(self):
        self.dirstack.push(self.clonedir)
        files = list(get_finder('svn')())
        self.failUnless(join('testpackage', 'subversion_only.py') in files)
        self.failUnless(join('testpackage', 'subversion_only.txt') in files)

    def testSubversionFinderEmptyDirname(self):
        self.dirstack.push(self.clonedir)
        files = list(get_finder('svn')(''))
        self.failUnless(join('testpackage', 'subversion_only.py') in files)
        self.failUnless(join('testpackage', 'subversion_only.txt') in files)

    def testSubversionSdistPy(self):
        st = Setuptools(defaults, Process(quiet=True))
        # This uses svn to create the manifest.
        archive = st.run_sdist(self.clonedir, [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'subversion_only.py'), True)

    def testSubversionSdistTxt(self):
        st = Setuptools(defaults, Process(quiet=True))
        # This uses svn to create the manifest.
        archive = st.run_sdist(self.clonedir, [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'subversion_only.txt'), True)

    def testDefaultSdistPy(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.destroy(self.clonedir)
        # This uses ??? to create the manifest.
        archive = st.run_sdist(self.clonedir, [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'subversion_only.py'), True)

    def testDefaultSdistTxt(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.destroy(self.clonedir)
        # This uses ??? to create the manifest. Note that the .txt file
        # is missing from the archive.
        archive = st.run_sdist(self.clonedir, [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'subversion_only.txt'), False)


class MercurialTests(MercurialSetup):

    def testMercurialFinder(self):
        self.clone()
        files = list(get_finder('hg')(self.clonedir))
        self.failUnless(join('testpackage', 'mercurial_only.py') in files)
        self.failUnless(join('testpackage', 'mercurial_only.txt') in files)

    def testMercurialFinderNoDirname(self):
        self.clone()
        self.dirstack.push(self.clonedir)
        files = list(get_finder('hg')())
        self.failUnless(join('testpackage', 'mercurial_only.py') in files)
        self.failUnless(join('testpackage', 'mercurial_only.txt') in files)

    def testMercurialFinderEmptyDirname(self):
        self.clone()
        self.dirstack.push(self.clonedir)
        files = list(get_finder('hg')(''))
        self.failUnless(join('testpackage', 'mercurial_only.py') in files)
        self.failUnless(join('testpackage', 'mercurial_only.txt') in files)

    def testMercurialSdistPy(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        # This uses hg to create the manifest.
        archive = st.run_sdist(self.clonedir, [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'mercurial_only.py'), True)

    def testMercurialSdistTxt(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        # This uses hg to create the manifest.
        archive = st.run_sdist(self.clonedir, [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'mercurial_only.txt'), True)


class GitTests(GitSetup):

    def testGitFinder(self):
        self.clone()
        self.dirstack.push(self.clonedir) # XXX
        files = list(get_finder('git')(self.clonedir))
        self.failUnless(join('testpackage', 'git_only.py') in files)
        self.failUnless(join('testpackage', 'git_only.txt') in files)

    def testGitFinderNoDirname(self):
        self.clone()
        self.dirstack.push(self.clonedir)
        files = list(get_finder('git')())
        self.failUnless(join('testpackage', 'git_only.py') in files)
        self.failUnless(join('testpackage', 'git_only.txt') in files)

    def testGitFinderEmptyDirname(self):
        self.clone()
        self.dirstack.push(self.clonedir)
        files = list(get_finder('git')(''))
        self.failUnless(join('testpackage', 'git_only.py') in files)
        self.failUnless(join('testpackage', 'git_only.txt') in files)

    def testGitSdistPy(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        # This uses git to create the manifest.
        archive = st.run_sdist(self.clonedir, [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'git_only.py'), True)

    def testGitSdistTxt(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        # This uses git to create the manifest.
        archive = st.run_sdist(self.clonedir, [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'git_only.txt'), True)

