import os
import tee

from os.path import abspath, join, isdir, isfile
from process import WithProcess
from python import WithPython
from dirstack import chdir
from exit import err_exit


class Setuptools(WithProcess, WithPython):
    """Interface to setuptools functions."""

    def __init__(self, defaults, process=None):
        WithProcess.__init__(self, process)
        WithPython.__init__(self, defaults.python)

    def is_valid_package(self, dir):
        return isfile(join(dir, 'setup.py'))

    def check_valid_package(self, dir):
        if not self.is_valid_package(dir):
            err_exit('Not eggified (no setup.py found): %(dir)s' % locals())

    @chdir
    def get_package_name(self, dir):
        python = self.python
        name = self.process.pipe(
            '"%(python)s" setup.py --name' % locals())
        if not name:
            err_exit('Bad setup.py')
        return name

    @chdir
    def get_package_version(self, dir):
        python = self.python
        version = self.process.pipe(
            '"%(python)s" setup.py --version' % locals())
        if not version:
            err_exit('Bad setup.py')
        return version

    @chdir
    def run_sdist(self, dir, sdistflags, quiet=False):
        python = self.python
        echo = True
        if quiet:
            echo = tee.NotAfter('running sdist')

        rc, lines = self.process.popen(
            '"%(python)s" setup.py sdist %(sdistflags)s' % locals(),
            echo=echo)

        if rc == 0:
            filename = self._parse_sdist_results(lines)
            if filename and isfile(filename):
                return abspath(filename)
        err_exit('Release failed')

    def _parse_sdist_results(self, lines):
        for line in lines:
            if line.startswith("creating 'dist") and "' and adding" in line:
                return line.split("'")[1]
        return ''

    @chdir
    def run_upload(self, dir, location, sdistflags, uploadflags):
        python = self.python

        rc, lines = self.process.popen(
            '"%(python)s" setup.py sdist %(sdistflags)s '
            'register --repository="%(location)s" '
            'upload --repository="%(location)s" %(uploadflags)s' % locals(),
            echo=tee.NotBefore('running register'))

        if rc == 0:
            register_ok, upload_ok = self._parse_upload_results(lines)
            if register_ok and upload_ok:
                return rc
        err_exit('Upload failed')

    def _parse_upload_results(self, lines):
        register_ok = upload_ok = False
        current, expect = None, 'running register'
        for line in lines:
            if line == expect:
                if line != 'Server response (200): OK':
                    current, expect = expect, 'Server response (200): OK'
                else:
                    if current == 'running register':
                        register_ok = True
                        current, expect = expect, 'running upload'
                    elif current == 'running upload':
                        upload_ok = True
                        current, expect = expect, None
        return register_ok, upload_ok

