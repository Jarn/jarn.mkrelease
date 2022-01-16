import os
import unittest

from os.path import exists

from jarn.mkrelease.setup import cleanup_pycache
from jarn.mkrelease.setup import walk_revctrl

from jarn.mkrelease.testing import JailSetup
from jarn.mkrelease.testing import GitSetup
from jarn.mkrelease.testing import quiet


class CleanupPyCacheTests(JailSetup):

    def test_cleanup_setup_pyc(self):
        self.mkfile('setup.pyc')
        self.assertTrue(exists('setup.pyc'))
        cleanup_pycache()
        self.assertFalse(exists('setup.pyc'))

    def test_cleanup_setup_pyo(self):
        self.mkfile('setup.pyo')
        self.assertTrue(exists('setup.pyo'))
        cleanup_pycache()
        self.assertFalse(exists('setup.pyo'))

    def test_cleanup_pycache_setup_pyc(self):
        os.mkdir('__pycache__')
        self.mkfile('__pycache__/setup..pyc')
        self.assertTrue(exists('__pycache__/setup..pyc'))
        cleanup_pycache()
        self.assertFalse(exists('__pycache__/setup..pyc'))
        self.assertFalse(exists('__pycache__'))

    def test_cleanup_pycache_setup_pyo(self):
        os.mkdir('__pycache__')
        self.mkfile('__pycache__/setup..pyo')
        self.assertTrue(exists('__pycache__/setup..pyo'))
        cleanup_pycache()
        self.assertFalse(exists('__pycache__/setup..pyo'))
        self.assertFalse(exists('__pycache__'))

    def test_cleanup_pycache_multi(self):
        os.mkdir('__pycache__')
        self.mkfile('__pycache__/setup.foo.pyc')
        self.mkfile('__pycache__/setup.bar.pyc')
        self.mkfile('__pycache__/setup.baz.pyo')
        self.assertTrue(exists('__pycache__/setup.foo.pyc'))
        self.assertTrue(exists('__pycache__/setup.bar.pyc'))
        self.assertTrue(exists('__pycache__/setup.baz.pyo'))
        cleanup_pycache()
        self.assertFalse(exists('__pycache__/setup.foo.pyc'))
        self.assertFalse(exists('__pycache__/setup.bar.pyc'))
        self.assertFalse(exists('__pycache__/setup.baz.pyo'))
        self.assertFalse(exists('__pycache__'))

    def test_cleanup_nothing(self):
        cleanup_pycache()

    def test_cleanup_empty_pycache(self):
        os.mkdir('__pycache__')
        self.assertTrue(exists('__pycache__'))
        cleanup_pycache()
        self.assertFalse(exists('__pycache__'))

    def test_ignore_setup_py(self):
        self.mkfile('setup.py')
        self.assertTrue(exists('setup.py'))
        cleanup_pycache()
        self.assertTrue(exists('setup.py'))

    def test_ignore_pycache_setup_py(self):
        os.mkdir('__pycache__')
        self.mkfile('__pycache__/setup..py')
        self.assertTrue(exists('__pycache__/setup..py'))
        cleanup_pycache()
        self.assertTrue(exists('__pycache__/setup..py'))
        self.assertTrue(exists('__pycache__'))

    def test_ignore_pycache_setup_py_while_cleaning_pyc(self):
        os.mkdir('__pycache__')
        self.mkfile('__pycache__/setup..pyc')
        self.mkfile('__pycache__/setup..py')
        self.assertTrue(exists('__pycache__/setup..pyc'))
        self.assertTrue(exists('__pycache__/setup..py'))
        cleanup_pycache()
        self.assertFalse(exists('__pycache__/setup..pyc'))
        self.assertTrue(exists('__pycache__/setup..py'))
        self.assertTrue(exists('__pycache__'))


class WalkRevctrlTests(GitSetup):

    def test_walk(self):
        self.assertEqual(sorted(walk_revctrl('testpackage', ff='git')), [
            'README.txt',
            'setup.py',
            'testpackage/__init__.py',
            'testpackage/git_only.c',
            'testpackage/git_only.py',
            'testpackage/git_only.txt'])

    def test_walk_curdir(self):
        self.dirstack.push('testpackage')
        self.assertEqual(sorted(walk_revctrl('', ff='git')), [
            'README.txt',
            'setup.py',
            'testpackage/__init__.py',
            'testpackage/git_only.c',
            'testpackage/git_only.py',
            'testpackage/git_only.txt'])

    def test_walk_curdir_explicit(self):
        self.dirstack.push('testpackage')
        self.assertEqual(sorted(walk_revctrl(os.curdir, ff='git')), [
            'README.txt',
            'setup.py',
            'testpackage/__init__.py',
            'testpackage/git_only.c',
            'testpackage/git_only.py',
            'testpackage/git_only.txt'])

    def test_walk_wrong_dir(self):
        #self.assertRaises(SystemExit, walk_revctrl, 'doesnotexist', ff='git')
        self.assertEqual(walk_revctrl('doesnotexist', ff='git'), [''])

    def test_walk_wrong_scm(self):
        #self.assertRaises(SystemExit, walk_revctrl, 'testpackage', ff='svn')
        self.assertEqual(walk_revctrl('testpackage', ff='svn'), [''])

    def test_walk_empty_scm(self):
        #self.assertRaises(SystemExit, walk_revctrl, 'testpackage', ff='')
        self.assertEqual(walk_revctrl('testpackage', ff=''), [''])

    def test_walk_unknown_scm(self):
        #self.assertRaises(SystemExit, walk_revctrl, 'testpackage', ff='cvs')
        self.assertEqual(walk_revctrl('testpackage', ff='cvs'), [''])

    def test_walk_none_scm(self):
        #self.assertRaises(SystemExit, walk_revctrl, 'testpackage', ff=None)
        self.assertEqual(walk_revctrl('testpackage', ff=None), [''])

