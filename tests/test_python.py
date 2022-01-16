import unittest
import sys

from jarn.mkrelease.python import Python

from jarn.mkrelease.testing import quiet


class PythonTests(unittest.TestCase):

    def testDefaults(self):
        python = Python()
        self.assertEqual(python.python, sys.executable)
        self.assertEqual(python.version_info, sys.version_info)

    def testArguments(self):
        python = Python(python='/foo/python', version_info=(2, 7, 0))
        self.assertEqual(python.python, '/foo/python')
        self.assertEqual(python.version_info, (2, 7, 0))

    def testStrCoerce(self):
        python = Python(python='/foo/python')
        self.assertEqual(str(python), '/foo/python')

    def test26IsValidPython(self):
        python = Python(version_info=(2, 6, 0))
        self.assertEqual(python.is_valid_python(), False)

    def test27IsValidPython(self):
        python = Python(version_info=(2, 7, 0))
        self.assertEqual(python.is_valid_python(), True)

    def test25IsInvalidPython(self):
        python = Python(version_info=(2, 5, 0))
        self.assertEqual(python.is_valid_python(), False)

    @quiet
    def testCheckValidPythonRaises(self):
        python = Python(version_info=(2, 5, 0))
        self.assertRaises(SystemExit, python.check_valid_python)

