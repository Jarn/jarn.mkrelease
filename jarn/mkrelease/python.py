import sys

from exit import err_exit


class Python(object):
    """Python interpreter abstraction."""

    def __init__(self, python=None, version_info=None):
        self.python = sys.executable
        self.version_info = sys.version_info
        if python is not None:
            self.python = python
        if version_info is not None:
            self.version_info = version_info

    def __str__(self):
        return self.python

    def is_valid_python(self):
        return (self.version_info[:2] >= (2, 6) and
                self.version_info[:2] < (3, 0))

    def check_valid_python(self):
        if not self.is_valid_python():
            err_exit('Python 2.6 or 2.7 required')
