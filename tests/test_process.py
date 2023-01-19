import unittest
import os

from jarn.mkrelease.process import Process

from jarn.mkrelease.testing import JailSetup
from jarn.mkrelease.testing import quiet


class PopenTests(unittest.TestCase):

    @quiet
    def test_simple(self):
        process = Process()
        rc, lines = process.popen('echo "Hello world"')
        self.assertEqual(rc, 0)
        self.assertEqual(lines, ['Hello world'])

    def test_quiet(self):
        process = Process(quiet=True)
        rc, lines = process.popen('echo "Hello world"')
        self.assertEqual(rc, 0)
        self.assertEqual(lines, ['Hello world'])

    def test_env(self):
        env = os.environ.copy()
        env['HELLO'] = 'Hello world'
        process = Process(quiet=True, env=env)
        rc, lines = process.popen('echo ${HELLO}')
        self.assertEqual(rc, 0)
        self.assertEqual(lines, ['Hello world'])

    def test_echo(self):
        process = Process()
        rc, lines = process.popen('echo "Hello world"', echo=False)
        self.assertEqual(rc, 0)
        self.assertEqual(lines, ['Hello world'])

    def test_echo2(self):
        process = Process()
        rc, lines = process.popen('$ "Hello world"', echo2=False)
        self.assertEqual(rc, 127)
        self.assertEqual(lines, [])

    @quiet
    def test_bad_cmd(self):
        process = Process()
        rc, lines = process.popen('$ "Hello world"')
        self.assertEqual(rc, 127)
        self.assertEqual(lines, [])

