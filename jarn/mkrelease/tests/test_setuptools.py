import os
import zipfile
import pkg_resources

from os.path import join, dirname

from jarn.mkrelease.setuptools import Setuptools
from jarn.mkrelease.process import Process

from jarn.mkrelease.testing import SubversionSetup
from jarn.mkrelease.testing import MercurialSetup
from jarn.mkrelease.testing import GitSetup


class defaults:
    python = 'python2.6'


class Env(dict):

    def __init__(self):
        # Put our hg and git support eggs onto the PYTHONPATH
        eggbase = join(dirname(__file__), 'testeggs')
        self.update(os.environ)
        self['PYTHONPATH'] = '%s:%s' % (
            join(eggbase, 'setuptools_hg-0.2x-py2.6.egg'),
            join(eggbase, 'setuptools_git-0.3.4x-py2.6.egg'))

env = Env()


def contains(archive, name):
    for info in zipfile.ZipFile(archive).infolist():
        if name in info.filename:
            return True
    return False


def file_finders():
    for ep in pkg_resources.iter_entry_points('setuptools.file_finders'):
        yield ep.load()


def get_finder(type):
    name = dict(git='gitlsfiles', hg='hg_file_finder', svn='_default_revctrl').get(type)
    for finder in file_finders():
        if finder.__name__ == name:
            return finder


class SubversionTests(SubversionSetup):

    def testSubversionFinder(self):
        st = Setuptools(defaults, Process(quiet=True))
        files = list(get_finder('svn')(self.clonedir))
        self.failUnless(join(self.clonedir, 'testpackage', 'subversion_only.py') in files)
        self.failUnless(join(self.clonedir, 'testpackage', 'subversion_only.txt') in files)

    def testSubversionSdistPy(self):
        st = Setuptools(defaults, Process(quiet=True))
        # This uses svn to create the manifest.
        archive = st.run_sdist(self.clonedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'subversion_only.py'), True)

    def testSubversionSdistTxt(self):
        st = Setuptools(defaults, Process(quiet=True))
        # This uses svn to create the manifest.
        archive = st.run_sdist(self.clonedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'subversion_only.txt'), True)

    def testDefaultSdistPy(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.destroy(self.clonedir)
        # This uses ??? to create the manifest.
        archive = st.run_sdist(self.clonedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'subversion_only.py'), True)

    def testDefaultSdistTxt(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.destroy(self.clonedir)
        # This uses ??? to create the manifest. Note that the .txt file
        # is missing from the archive.
        archive = st.run_sdist(self.clonedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'subversion_only.txt'), False)


class MercurialTests(MercurialSetup):

    def testMercurialFinder(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        files = list(get_finder('hg')(self.clonedir))
        self.failUnless(join('testpackage', 'mercurial_only.py') in files)
        self.failUnless(join('testpackage', 'mercurial_only.txt') in files)

    def testMercurialSdistPy(self):
        st = Setuptools(defaults, Process(quiet=True, env=env))
        self.clone()
        # This uses hg to create the manifest.
        archive = st.run_sdist(self.clonedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'mercurial_only.py'), True)

    def testMercurialSdistTxt(self):
        st = Setuptools(defaults, Process(quiet=True, env=env))
        self.clone()
        # This uses hg to create the manifest.
        archive = st.run_sdist(self.clonedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'mercurial_only.txt'), True)


class GitTests(GitSetup):

    def testGitFinder(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        files = list(get_finder('git')(self.clonedir))
        self.failUnless(join('testpackage', 'git_only.py') in files)
        self.failUnless(join('testpackage', 'git_only.txt') in files)

    def testGitSdistPy(self):
        st = Setuptools(defaults, Process(quiet=True, env=env))
        self.clone()
        # This uses git to create the manifest.
        archive = st.run_sdist(self.clonedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'git_only.py'), True)

    def testGitSdistTxt(self):
        st = Setuptools(defaults, Process(quiet=True, env=env))
        self.clone()
        # This uses git to create the manifest.
        archive = st.run_sdist(self.clonedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'git_only.txt'), True)

