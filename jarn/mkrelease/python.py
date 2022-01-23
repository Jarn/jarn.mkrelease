from __future__ import absolute_import

import sys

from .exit import err_exit


class Python(object):
    """Python interpreter abstraction."""

    def __init__(self, python=None, version_info=None):
        self.python = python or sys.executable
        self.version_info = version_info or sys.version_info

    def __str__(self):
        return self.python

    def is_valid_python(self):
        return (self.version_info[:2] >= (2, 7))

    def check_valid_python(self):
        if not self.is_valid_python():
            err_exit('mkrelease: Python >= 2.7 required')

