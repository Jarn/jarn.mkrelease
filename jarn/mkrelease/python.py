import sys

from exit import err_exit


class Python(object):
    """Python interpreter abstraction."""

    @property
    def python(self):
        return sys.executable

    def __str__(self):
        return self.python

    def is_valid_python(self):
        return sys.version_info[:2] >= (2, 6)

    def check_valid_python(self):
        if not self.is_valid_python():
            err_exit('Python >= 2.6 required')
