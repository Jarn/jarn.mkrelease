import os
import shutil
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

    def testSubversionSdist(self):
        st = Setuptools(defaults, Process(quiet=True))
        # This uses svn to create the manifest, obviously.
        archive = st.run_sdist(self.clonedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'subversion_only.py'), True)


class SubversionMercurialTests(MercurialSetup):

    def testMercurialSdist(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.destroy(name='svn')
        # This uses hg to create the manifest.
        archive = st.run_sdist(self.packagedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'mercurial_only.py'), True)

    def testMercurialPreemptsSubversion(self):
        st = Setuptools(defaults, Process(quiet=True))
        # This uses hg to create the manifest.
        archive = st.run_sdist(self.packagedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'mercurial_only.py'), True)


class SubversionGitTests(GitSetup):

    def testGitSdist(self):
        st = Setuptools(defaults, Process(quiet=True))
        self.destroy(name='svn')
        # This uses git to create the manifest.
        archive = st.run_sdist(self.packagedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'git_only.py'), True)

    def testGitPreemptsSubversion(self):
        st = Setuptools(defaults, Process(quiet=True))
        # This uses git to create the manifest.
        archive = st.run_sdist(self.packagedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'git_only.py'), True)


class GitMercurialTests(GitSetup):

    def setUp(self):
        GitSetup.setUp(self)
        try:
            shutil.copytree(join(dirname(__file__), MercurialSetup.source, '.hg'),
                            join(self.packagedir, '.hg'))
            self.destroy(self.packagedir, name='svn')
        except:
            self.cleanUp()
            raise

    def testGitPreemptsMercurial(self):
        st = Setuptools(defaults, Process(quiet=True))
        # This uses git to create the manifest.
        archive = st.run_sdist(self.packagedir, '--formats=zip', True)
        self.assertEqual(contains(archive, 'git_only.py'), True)

