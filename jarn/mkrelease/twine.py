from __future__ import absolute_import
from __future__ import print_function

import sys
import os

from os.path import expanduser

import setuptools # XXX
import distutils.spawn

from .process import Process
from .python import Python
from .chdir import chdir
from .exit import err_exit
from .tee import *
from .tee import run, system
from .colors import bold


class Twine(object):
    """Interface to twine."""

    def __init__(self, process=None, twine=None, defaults=None):
        self._twine = None
        self._interactive = None
        self._defaults = defaults
        self._process = process

        self.process = None
        self.python = Python()
        self.twine = twine

        if defaults and not defaults.interactive:
            self.interactive = False
        else:
            self.interactive = True

    @property
    def twine(self):
        return self._twine

    @twine.setter
    def twine(self, value):
        self._twine = self._get_executable(value, self._defaults)

    @property
    def interactive(self):
        return self._interactive

    @interactive.setter
    def interactive(self, value):
        self._interactive = value
        self.process = self._process or self._get_process(value)

    def _get_executable(self, twine, defaults):
        # 1. Value of --twine command line option, or
        # 2. Value of TWINE environment variable, or
        # 3. Value of 'twine' configuration file setting, or
        # 4. 'python -m twine' if twine is importable, or
        # 5. 'twine'
        if twine:
            return expanduser(twine)
        if os.environ.get('TWINE'):
            return expanduser(os.environ.get('TWINE'))
        if defaults and defaults.twine:
            return expanduser(defaults.twine)
        try:
            import twine
            return 'python -m twine'
        except ImportError:
            return 'twine'

    def _get_process(self, interactive):
        return Process(
            env=self.get_env(),
            runner=system if interactive else run)

    def get_env(self):
        # Make sure twine and its dependencies are found if mkrelease
        # has been installed with zc.buildout
        env = os.environ.copy()
        if self.twine == 'python -m twine':
            env['PYTHONPATH'] = ':'.join(sys.path)
        elif 'PYTHONPATH' in env:
            del env['PYTHONPATH']
        return env

    def is_valid_twine(self):
        if self.twine == 'python -m twine':
            return True
        if distutils.spawn.find_executable(self.twine):
            return True
        return False

    def check_valid_twine(self):
        if not self.is_valid_twine():
            err_exit('mkrelease: Command not found: %s' % (self.twine,))

    @chdir
    def run_register(self, directory, distfiles, location, quiet=False):
        if not self.process.quiet:
            print(bold('running twine_register'))

        echo = And(NotEmpty(), Before('View at:'))
        if quiet:
            echo = StartsWith('Registering')

        echo2 = On()

        serverflags = ['--repository="%(location)s"' % locals()]
        if not self.interactive:
            serverflags = ['--non-interactive'] + serverflags
        if quiet or not self.interactive:
            serverflags = ['--disable-progress-bar'] + serverflags

        # Prefer sdists
        sdistfiles = [x for x in distfiles if x.endswith(('.zip', '.tar.gz'))]
        if sdistfiles:
            distfiles = sdistfiles[:1]
        else:
            distfiles = distfiles[:1]
        distfiles = [('"%s"' % x) for x in distfiles]

        rc, lines = self._run_twine(
            ['register'] + serverflags + distfiles,
            echo=echo,
            echo2=echo2)

        if rc == 0:
            return rc
        err_exit('ERROR: register failed')

    @chdir
    def run_upload(self, directory, distfiles, location, uploadflags, quiet=False):
        if not self.process.quiet:
            print(bold('running twine_upload'))

        echo = And(NotEmpty(), Before('View at:'))
        if quiet:
            echo = StartsWith('Uploading')

        echo2 = On()

        serverflags = ['--repository="%(location)s"' % locals()]
        if not self.interactive:
            serverflags = ['--non-interactive'] + serverflags
        if quiet or not self.interactive:
            serverflags = ['--disable-progress-bar'] + serverflags

        distfiles = [('"%s"' % x) for x in distfiles]

        rc, lines = self._run_twine(
            ['upload'] + serverflags + uploadflags + distfiles,
            echo=echo,
            echo2=echo2)

        if rc == 0:
            return rc
        err_exit('ERROR: upload failed')

    def _run_twine(self, args, echo=True, echo2=True):
        twine = self.twine
        python = self.python

        if twine == 'python -m twine':
            twine = '"%(python)s" -m twine' % locals()
        else:
            twine = '"%(twine)s"' % locals()

        args = ['--no-color'] + args

        return self.process.popen(
            '%s %s' % (twine, ' '.join(args)),
            echo=echo,
            echo2=echo2)

