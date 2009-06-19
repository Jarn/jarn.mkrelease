import os
import zipfile

from os.path import join, dirname

from jarn.mkrelease.setuptools import Setuptools
from jarn.mkrelease.process import Process

from jarn.mkrelease.testing import SubversionSetup
from jarn.mkrelease.testing import MercurialSetup
from jarn.mkrelease.testing import GitSetup


class defaults:
    python = 'python2.6'


def contains(archive, name):
    for info in zipfile.ZipFile(archive).infolist():
        if name in info.filename:
            return True
    return False


class SubversionTests(SubversionSetup):

    def testSubversionSdistPy(self):
        st = Setuptools(defaults, Process(quiet=True))
        # This uses svn to create the manifest.
        archive = st.run_sdist(self.clonedir, '--formats=zip', True)
        self.assertEqual(contains(archive, '__init__.py'), True)

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
        self.assertEqual(contains(archive, '__init__.py'), True)

    def testDefaultSdistTxt(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.destroy(self.clonedir)
        # This uses ??? to create the manifest.
        archive = st.run_sdist(self.clonedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'subversion_only.txt'), False)


class MercurialTests(MercurialSetup):

    def testMercurialSdistPy(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        # This uses hg to create the manifest.
        archive = st.run_sdist(self.clonedir, '--formats=zip', True)
        self.assertEqual(contains(archive, '__init__.py'), True)

    def testMercurialSdistTxt(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        # This uses hg to create the manifest.
        archive = st.run_sdist(self.clonedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'mercurial_only.txt'), True)


class GitTests(GitSetup):

    def testGitSdistPy(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        # This uses git to create the manifest.
        archive = st.run_sdist(self.clonedir, '--formats=zip', True)
        self.assertEqual(contains(archive, '__init__.py'), True)

    def testGitSdistTxt(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.clone()
        # This uses git to create the manifest.
        archive = st.run_sdist(self.clonedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'git_only.txt'), True)

