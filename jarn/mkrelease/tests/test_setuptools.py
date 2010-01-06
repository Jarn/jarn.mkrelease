import sys
import os
import zipfile
import pkg_resources

from os.path import join, isfile

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


def manifest(archive):
    manifest = zipfile.ZipFile(archive).open(
        'testpackage-2.6/testpackage.egg-info/SOURCES.txt')
    return manifest.read()


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
        archive = st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'subversion_only.py'), True)

    def testSubversionSdistTxt(self):
        st = Setuptools(defaults, Process(quiet=True))
        # This uses svn to create the manifest.
        archive = st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'subversion_only.txt'), True)

    def testDefaultSdistPy(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.destroy(self.clonedir)
        # This uses ??? to create the manifest.
        archive = st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'subversion_only.py'), True)

    def testDefaultSdistTxt(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.destroy(self.clonedir)
        # This uses ??? to create the manifest. Note that the .txt file
        # is missing from the archive.
        archive = st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'subversion_only.txt'), False)

    def testSubversionMetaFile(self):
        st = Setuptools(defaults, Process(quiet=True))
        # This uses svn to create the manifest.
        archive = st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'], scmtype='svn')
        self.assertEqual(contains(archive, '.svnignore'), False)

    def testSubversionManifest(self):
        st = Setuptools(defaults, Process(quiet=True))
        # This uses svn to create the manifest.
        archive = st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'], scmtype='svn')
        self.assertEqual(manifest(archive), """\
README.txt
setup.py
testpackage/__init__.py
testpackage/subversion_only.py
testpackage/subversion_only.txt
testpackage.egg-info/PKG-INFO
testpackage.egg-info/SOURCES.txt
testpackage.egg-info/dependency_links.txt
testpackage.egg-info/not-zip-safe
testpackage.egg-info/requires.txt
testpackage.egg-info/top_level.txt""")

    def testRemoveSetupPyc(self):
        st = Setuptools(defaults, Process(quiet=True))
        st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'], scmtype='svn')
        self.failIf(isfile(join(self.clonedir, 'setup.pyc')))


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
        archive = st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'mercurial_only.py'), True)

    def testMercurialSdistTxt(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        # This uses hg to create the manifest.
        archive = st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'mercurial_only.txt'), True)

    def testMercurialMetaFile(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        # This uses hg to create the manifest.
        archive = st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'], scmtype='hg')
        self.assertEqual(contains(archive, '.hgignore'), False)

    def testMercurialManifest(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        # This uses hg to create the manifest.
        archive = st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'], scmtype='hg')
        self.assertEqual(manifest(archive), """\
README.txt
setup.py
testpackage/__init__.py
testpackage/mercurial_only.py
testpackage/mercurial_only.txt
testpackage.egg-info/PKG-INFO
testpackage.egg-info/SOURCES.txt
testpackage.egg-info/dependency_links.txt
testpackage.egg-info/not-zip-safe
testpackage.egg-info/requires.txt
testpackage.egg-info/top_level.txt""")

    def testRemoveSetupPyc(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'], scmtype='hg')
        self.failIf(isfile(join(self.clonedir, 'setup.pyc')))


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
        archive = st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'git_only.py'), True)

    def testGitSdistTxt(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        # This uses git to create the manifest.
        archive = st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'])
        self.assertEqual(contains(archive, 'git_only.txt'), True)

    def testGitMetaFile(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        # This uses git to create the manifest.
        archive = st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'], scmtype='git')
        self.assertEqual(contains(archive, '.gitignore'), False)

    def testGitManifest(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        # This uses git to create the manifest.
        archive = st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'], scmtype='git')
        self.assertEqual(manifest(archive), """\
README.txt
setup.py
testpackage/__init__.py
testpackage/git_only.py
testpackage/git_only.txt
testpackage.egg-info/PKG-INFO
testpackage.egg-info/SOURCES.txt
testpackage.egg-info/dependency_links.txt
testpackage.egg-info/not-zip-safe
testpackage.egg-info/requires.txt
testpackage.egg-info/top_level.txt""")

    def testRemoveSetupPyc(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        st.run_dist(self.clonedir, 'sdist', [], ['--formats=zip'], scmtype='git')
        self.failIf(isfile(join(self.clonedir, 'setup.pyc')))

