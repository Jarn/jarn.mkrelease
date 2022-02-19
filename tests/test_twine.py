import os
import stat
import unittest

from os.path import join, expanduser

from jarn.mkrelease.twine import Twine

from jarn.mkrelease.testing import JailSetup
from jarn.mkrelease.testing import setenv, delenv
from jarn.mkrelease.testing import quiet


# Is twine importable?
try:
    import twine
    importable = True
    del twine
except ImportError:
    importable = False


class SelectTwineTests(unittest.TestCase):

    def testDirect(self):
        tw = Twine(twine='my.exe')
        self.assertEqual(tw.twine, 'my.exe')

    def testEnvironment(self):
        with setenv('TWINE', 'my.exe'):
            tw = Twine()
            self.assertEqual(tw.twine, 'my.exe')

    def testConfig(self):
        with delenv('TWINE'):
            class config:
                twine = 'my.exe'
            tw = Twine(defaults=config)
            self.assertEqual(tw.twine, 'my.exe')

    def testExpandUserDirect(self):
        tw = Twine(twine='~/my.exe')
        self.assertEqual(tw.twine, expanduser('~/my.exe'))

    def testExpandUserEnvironment(self):
        with setenv('TWINE', '~/my.exe'):
            tw = Twine()
            self.assertEqual(tw.twine, expanduser('~/my.exe'))

    def testExpandUserConfig(self):
        with delenv('TWINE'):
            class config:
                twine = '~/my.exe'
            tw = Twine(defaults=config)
            self.assertEqual(tw.twine, expanduser('~/my.exe'))

    def testDirectBeforeEnvironment(self):
        with setenv('TWINE', 'other.exe'):
            tw = Twine(twine='my.exe')
            self.assertEqual(tw.twine, 'my.exe')

    def testEnvironmentBeforeConfig(self):
        with setenv('TWINE', 'my.exe'):
            class config:
                twine = 'other.exe'
            tw = Twine(defaults=config)
            self.assertEqual(tw.twine, 'my.exe')

    def testConfigBeforeDefault(self):
        with delenv('TWINE'):
            class config:
                twine = 'my.exe'
            tw = Twine(defaults=config)
            self.assertEqual(tw.twine, 'my.exe')

    def testDefault(self):
        with delenv('TWINE'):
            tw = Twine()
            self.assertEqual(tw.twine, 'python -m twine' if importable else 'twine')


class ValidTwineTests(JailSetup):

    def mkexe(self, name):
        self.mkfile(name, """\
#!/bin/sh
echo ok
""")
        os.chmod(name, stat.S_IRWXU)

    def testImportableValid(self):
        with setenv('PATH', self.tempdir):
            tw = Twine(twine='python -m twine')
            self.assertEqual(tw.is_valid_twine(), True)

    def testExecutableValid(self):
        with setenv('PATH', self.tempdir):
            self.mkexe('my.exe')
            tw = Twine(twine='my.exe')
            self.assertEqual(tw.is_valid_twine(), True)

    def testExecutableInvalid(self):
        with setenv('PATH', self.tempdir):
            tw = Twine(twine='my.exe')
            self.assertEqual(tw.is_valid_twine(), False)

    def testFullPathValid(self):
        self.mkexe('my.exe')
        tw = Twine(twine=join(self.tempdir, 'my.exe'))
        self.assertEqual(tw.is_valid_twine(), True)

    def testFullPathInvalid(self):
        tw = Twine(twine=join(self.tempdir, 'my.exe'))
        self.assertEqual(tw.is_valid_twine(), False)

    @quiet
    def testCheckRaises(self):
        with setenv('PATH', self.tempdir):
            tw = Twine(twine='my.exe')
            self.assertRaises(SystemExit, tw.check_valid_twine)

    def testDefaultValid(self):
        with setenv('PATH', self.tempdir), delenv('TWINE'):
            self.mkexe('twine')
            tw = Twine()
            self.assertEqual(tw.twine, 'python -m twine' if importable else 'twine')
            self.assertEqual(tw.is_valid_twine(), True)

