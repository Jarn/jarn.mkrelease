import sys
import os
import zipfile
import pkg_resources
import unittest

from os.path import join, isfile
from contextlib import closing

from jarn.mkrelease.setuptools import Setuptools
from jarn.mkrelease.process import Process
from jarn.mkrelease.utils import decode

from jarn.mkrelease.testing import SubversionSetup
from jarn.mkrelease.testing import MercurialSetup
from jarn.mkrelease.testing import GitSetup


def contains(archive, name):
    for info in zipfile.ZipFile(archive).infolist():
        if name in info.filename:
            return True
    return False


def get_manifest(archive):
    with closing(zipfile.ZipFile(archive).open(
        'testpackage-2.6/testpackage.egg-info/SOURCES.txt')) as manifest:
        text = manifest.read()
        if sys.version_info[0] >= 3:
            return decode(text, errors='strict')
        return text


def get_finder(type):
    for ep in pkg_resources.iter_entry_points('setuptools.file_finders'):
        if type == ep.name:
            return ep.load()


def get_env():
    return Setuptools().get_env()


class SubversionTests(SubversionSetup):

    def testSubversionFinder(self):
        self.dirstack.push(self.clonedir) # XXX
        files = list(get_finder('svn')(self.clonedir))
        if self.scm.version_info[:2] >= (1, 7):
            self.assertTrue(join('testpackage', 'subversion_only.py') in files)
            self.assertTrue(join('testpackage', 'subversion_only.txt') in files)
        else:
            self.assertTrue(join(self.clonedir, 'testpackage', 'subversion_only.py') in files)
            self.assertTrue(join(self.clonedir, 'testpackage', 'subversion_only.txt') in files)

    def testSubversionFinderNoArg(self):
        self.dirstack.push(self.clonedir)
        files = list(get_finder('svn')())
        self.assertTrue(join('testpackage', 'subversion_only.py') in files)
        self.assertTrue(join('testpackage', 'subversion_only.txt') in files)

    def testSubversionFinderEmptyArg(self):
        self.dirstack.push(self.clonedir)
        files = list(get_finder('svn')(''))
        self.assertTrue(join('testpackage', 'subversion_only.py') in files)
        self.assertTrue(join('testpackage', 'subversion_only.txt') in files)

    def testSubversionSdistPy(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.clonedir, [], 'sdist', ['--formats=zip'], ff='svn')
        self.assertEqual(contains(archive, 'subversion_only.py'), True)

    def testSubversionSdistTxt(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.clonedir, [], 'sdist', ['--formats=zip'], ff='svn')
        self.assertEqual(contains(archive, 'subversion_only.txt'), True)

    def testSubversionSdistC(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.clonedir, [], 'sdist', ['--formats=zip'], ff='svn')
        self.assertEqual(contains(archive, 'subversion_only.c'), True)

    def testDefaultSdistPy(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        self.destroy(self.clonedir)
        # Use the default file-finder to create the manifest
        archive = st.run_dist(self.clonedir, [], 'sdist', ['--formats=zip'])
        self.assertEqual(contains(archive, 'subversion_only.py'), True)

    def testDefaultSdistTxt(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        self.destroy(self.clonedir)
        # Use the default file-finder to create the manifest; .txt file is missing.
        archive = st.run_dist(self.clonedir, [], 'sdist', ['--formats=zip'])
        self.assertEqual(contains(archive, 'subversion_only.txt'), False)

    def testDefaultSdistC(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        self.destroy(self.clonedir)
        # Use the default file-finder to create the manifest; .c file is missing.
        archive = st.run_dist(self.clonedir, [], 'sdist', ['--formats=zip'])
        self.assertEqual(contains(archive, 'subversion_only.c'), False)

    def testSubversionMetaFile(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.clonedir, [], 'sdist', ['--formats=zip'], ff='svn')
        self.assertEqual(contains(archive, '.svnignore'), False)

    def testSubversionManifest(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.clonedir, [], 'sdist', ['--formats=zip'], ff='svn')
        self.assertEqual(get_manifest(archive), """\
README.txt
setup.py
testpackage/__init__.py
testpackage/subversion_only.c
testpackage/subversion_only.py
testpackage/subversion_only.txt
testpackage.egg-info/PKG-INFO
testpackage.egg-info/SOURCES.txt
testpackage.egg-info/dependency_links.txt
testpackage.egg-info/not-zip-safe
testpackage.egg-info/requires.txt
testpackage.egg-info/top_level.txt""")

    def testRemoveSetupPyc(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        st.run_dist(self.clonedir, [], 'sdist', ['--formats=zip'], ff='svn')
        self.assertFalse(isfile(join(self.clonedir, 'setup.pyc')))

    def testInfoFlags(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.clonedir, st.infoflags, 'sdist', ['--formats=zip'], ff='svn')
        self.assertEqual(contains(archive, 'subversion_only.py'), True)


class MercurialTests(MercurialSetup):

    def testMercurialFinder(self):
        files = list(get_finder('hg')(self.packagedir))
        self.assertTrue(join('testpackage', 'mercurial_only.py') in files)
        self.assertTrue(join('testpackage', 'mercurial_only.txt') in files)

    def testMercurialFinderNoArg(self):
        self.dirstack.push(self.packagedir)
        files = list(get_finder('hg')())
        self.assertTrue(join('testpackage', 'mercurial_only.py') in files)
        self.assertTrue(join('testpackage', 'mercurial_only.txt') in files)

    def testMercurialFinderEmptyArg(self):
        self.dirstack.push(self.packagedir)
        files = list(get_finder('hg')(''))
        self.assertTrue(join('testpackage', 'mercurial_only.py') in files)
        self.assertTrue(join('testpackage', 'mercurial_only.txt') in files)

    def testMercurialSdistPy(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='hg')
        self.assertEqual(contains(archive, 'mercurial_only.py'), True)

    def testMercurialSdistTxt(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='hg')
        self.assertEqual(contains(archive, 'mercurial_only.txt'), True)

    def testMercurialSdistC(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='hg')
        self.assertEqual(contains(archive, 'mercurial_only.c'), True)

    def testMercurialMetaFile(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='hg')
        self.assertEqual(contains(archive, '.hgignore'), False)

    def testMercurialManifest(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='hg')
        self.assertEqual(get_manifest(archive), """\
README.txt
setup.py
testpackage/__init__.py
testpackage/mercurial_only.c
testpackage/mercurial_only.py
testpackage/mercurial_only.txt
testpackage.egg-info/PKG-INFO
testpackage.egg-info/SOURCES.txt
testpackage.egg-info/dependency_links.txt
testpackage.egg-info/not-zip-safe
testpackage.egg-info/requires.txt
testpackage.egg-info/top_level.txt""")

    def testRemoveSetupPyc(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='hg')
        self.assertFalse(isfile(join(self.packagedir, 'setup.pyc')))

    def testInfoFlags(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, st.infoflags, 'sdist', ['--formats=zip'], ff='hg')
        self.assertEqual(contains(archive, 'mercurial_only.py'), True)


class GitTests(GitSetup):

    def testGitFinder(self):
        self.dirstack.push(self.packagedir) # XXX
        files = list(get_finder('git')(self.packagedir))
        self.assertTrue(join('testpackage', 'git_only.py') in files)
        self.assertTrue(join('testpackage', 'git_only.txt') in files)

    def testGitFinderNoArg(self):
        self.dirstack.push(self.packagedir)
        files = list(get_finder('git')())
        self.assertTrue(join('testpackage', 'git_only.py') in files)
        self.assertTrue(join('testpackage', 'git_only.txt') in files)

    def testGitFinderEmptyArg(self):
        self.dirstack.push(self.packagedir)
        files = list(get_finder('git')(''))
        self.assertTrue(join('testpackage', 'git_only.py') in files)
        self.assertTrue(join('testpackage', 'git_only.txt') in files)

    def testGitSdistPy(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='git')
        self.assertEqual(contains(archive, 'git_only.py'), True)

    def testGitSdistTxt(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='git')
        self.assertEqual(contains(archive, 'git_only.txt'), True)

    def testGitSdistC(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='git')
        self.assertEqual(contains(archive, 'git_only.c'), True)

    def testGitMetaFile(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='git')
        self.assertEqual(contains(archive, '.gitignore'), False)

    def testGitManifest(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='git')
        self.assertEqual(get_manifest(archive), """\
README.txt
setup.py
testpackage/__init__.py
testpackage/git_only.c
testpackage/git_only.py
testpackage/git_only.txt
testpackage.egg-info/PKG-INFO
testpackage.egg-info/SOURCES.txt
testpackage.egg-info/dependency_links.txt
testpackage.egg-info/not-zip-safe
testpackage.egg-info/requires.txt
testpackage.egg-info/top_level.txt""")

    def testRemoveSetupPyc(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='git')
        self.assertFalse(isfile(join(self.packagedir, 'setup.pyc')))

    def testInfoFlags(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, st.infoflags, 'sdist', ['--formats=zip'], ff='git')
        self.assertEqual(contains(archive, 'git_only.py'), True)


class NoneTests(GitSetup):

    def testNoneSdistPy(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='none')
        self.assertEqual(contains(archive, 'git_only.py'), True)

    def testNoneSdistTxt(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='none')
        self.assertEqual(contains(archive, 'git_only.txt'), False)

    def testNoneSdistC(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='none')
        self.assertEqual(contains(archive, 'git_only.c'), False)

    def testNoneMetaFile(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='none')
        self.assertEqual(contains(archive, '.gitignore'), False)

    def testNoneManifest(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='none')
        self.assertEqual(get_manifest(archive), """\
README.txt
setup.py
testpackage/__init__.py
testpackage/git_only.py
testpackage.egg-info/PKG-INFO
testpackage.egg-info/SOURCES.txt
testpackage.egg-info/dependency_links.txt
testpackage.egg-info/not-zip-safe
testpackage.egg-info/requires.txt
testpackage.egg-info/top_level.txt""")

    def testRemoveSetupPyc(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='none')
        self.assertFalse(isfile(join(self.packagedir, 'setup.pyc')))


class ManifestInTests(GitSetup):

    def setUp(self):
        GitSetup.setUp(self)
        self.manifest_in = join(self.packagedir, 'MANIFEST.in')
        self.mkfile(self.manifest_in, 'recursive-include testpackage *.c')

    def testManifestSdistPy(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='none')
        self.assertEqual(contains(archive, 'git_only.py'), True)

    def testManifestSdistTxt(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='none')
        self.assertEqual(contains(archive, 'git_only.txt'), False)

    def testManifestSdistC(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='none')
        self.assertEqual(contains(archive, 'git_only.c'), True)

    def testManifestMetaFile(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='none')
        self.assertEqual(contains(archive, '.gitignore'), False)

    def testManifestManifest(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        archive = st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='none')
        self.assertEqual(get_manifest(archive), """\
MANIFEST.in
README.txt
setup.py
testpackage/__init__.py
testpackage/git_only.c
testpackage/git_only.py
testpackage.egg-info/PKG-INFO
testpackage.egg-info/SOURCES.txt
testpackage.egg-info/dependency_links.txt
testpackage.egg-info/not-zip-safe
testpackage.egg-info/requires.txt
testpackage.egg-info/top_level.txt""")

    def testRemoveSetupPyc(self):
        st = Setuptools(Process(quiet=True, env=get_env()))
        st.run_dist(self.packagedir, [], 'sdist', ['--formats=zip'], ff='none')
        self.assertFalse(isfile(join(self.packagedir, 'setup.pyc')))

