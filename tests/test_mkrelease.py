# THIS SHOULD BE DOCTESTS
import sys
import os

from os import listdir
from os.path import join

from jarn.mkrelease.mkrelease import main

from jarn.mkrelease.testing import GitSetup
from jarn.mkrelease.testing import quiet
from jarn.mkrelease.testing import setenv

PY = sys.version_info[0]


class FunctionalTests(GitSetup):

    def mkrelease(self, args):
        with setenv('JARN_RUN', '1'):
            return main(args)

    @quiet
    def test_gztar_release(self):
        rc = self.mkrelease(['-n', '-q', '-m', '-g', 'testpackage'])
        self.assertEqual(rc, 0)
        self.assertEqual(listdir(join('testpackage', 'dist')), ['testpackage-2.6.tar.gz'])

    @quiet
    def test_zip_release(self):
        rc = self.mkrelease(['-n', '-q', '-m', '-z', 'testpackage'])
        self.assertEqual(rc, 0)
        self.assertEqual(listdir(join('testpackage', 'dist')), ['testpackage-2.6.zip'])

    @quiet
    def test_wheel_release(self):
        rc = self.mkrelease(['-n', '-q', '-m', '-w', 'testpackage'])
        self.assertEqual(rc, 0)
        self.assertEqual(listdir(join('testpackage', 'dist')), ['testpackage-2.6-py%d-none-any.whl' % PY])

    @quiet
    def test_development_release(self):
        self.mkfile(join('testpackage', 'setup.cfg'), """\
[egg_info]
tag_build = dev0
""")
        rc = self.mkrelease(['-n', '-q', '-m', '-g', '-e', 'testpackage'])
        self.assertEqual(rc, 0)
        self.assertEqual(listdir(join('testpackage', 'dist')), ['testpackage-2.6.dev0.tar.gz'])

    @quiet
    def test_non_development_release(self):
        self.mkfile(join('testpackage', 'setup.cfg'), """\
[egg_info]
tag_build = dev0
""")
        rc = self.mkrelease(['-n', '-q', '-m', '-g', 'testpackage'])
        self.assertEqual(rc, 0)
        self.assertEqual(listdir(join('testpackage', 'dist')), ['testpackage-2.6.tar.gz'])

    @quiet
    def test_no_sandbox(self):
        rc = self.mkrelease(['-n', '-q', '.'])
        self.assertEqual(rc, 1)

    @quiet
    def test_no_setup_py(self):
        os.remove(join('testpackage', 'setup.py'))
        rc = self.mkrelease(['-n', '-q', 'testpackage'])
        self.assertEqual(rc, 1)

    @quiet
    def test_no_setup_py_but_setup_cfg(self):
        os.remove(join('testpackage', 'setup.py'))
        self.mkfile(join('testpackage', 'setup.cfg'), """\
[metadata]
name = testpackage
version = 2.7
url = https://github.com/me/testpackage
author = My Name
author_email = me@example.com

[options]
packages = find:
""")
        rc = self.mkrelease(['-n', '-q', '-m', '-g', 'testpackage'])
        self.assertEqual(rc, 0)
        self.assertEqual(listdir(join('testpackage', 'dist')), ['testpackage-2.7.tar.gz'])

