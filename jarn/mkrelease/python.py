from process import Process
from exit import err_exit


class Python(object):
    """A Python interpreter path that can test itself."""

    def __init__(self, defaults, process=None):
        self.process = process or Process()
        self.python = defaults.python

    def __str__(self):
        return self.python

    def is_valid_python(self, python=None):
        version = self.get_python_version(python)
        if version and version >= '2.6':
            return True
        return False

    def check_valid_python(self, python=None):
        version = self.get_python_version(python)
        if not version:
            err_exit('Bad interpreter')
        if version < '2.6':
            err_exit('Python >= 2.6 required')

    def get_python_version(self, python=None):
        if python is None:
            python = self.python
        version = self.process.pipe(
            '"%(python)s" -c"import sys; print sys.version[:3]"' % locals())
        return version

