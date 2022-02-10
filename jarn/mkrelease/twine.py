from __future__ import absolute_import
from __future__ import print_function

import os

from os.path import expanduser

from .process import Process
from .python import Python
from .chdir import chdir
from .exit import err_exit
from .tee import *
from .colors import bold


class Twine(object):
    """Interface to twine."""

    def __init__(self, process=None, twine=None, defaults=None):
        self.process = process or Process()
        self.python = Python()
        self.twine = self._get_executable(twine, defaults)

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

    @chdir
    def run_register(self, directory, distfiles, location, quiet=False):
        if not self.process.quiet:
            print(bold('running twine_register'))

        echo = NotEmpty()
        if quiet:
            echo = And(echo, StartsWith('Registering'))
        else:
            echo = And(echo, Before('View at:'))

        echo2 = True

        serverflags = ['--repository="%(location)s"' % locals()]

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

        echo = NotEmpty()
        if quiet:
            echo = And(echo, StartsWith('Uploading'))
        else:
            echo = And(echo, Before('View at:'))

        echo2 = True

        serverflags = ['--repository="%(location)s"' % locals()]
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

        cmd = '%s %s' % (twine, ' '.join(args))

        return self.process.popen(cmd, echo=echo, echo2=echo2)

