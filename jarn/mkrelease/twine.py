from __future__ import absolute_import
from __future__ import print_function

from .process import Process
from .chdir import chdir
from .exit import err_exit
from .tee import *
from .colors import bold


class Twine(object):
    """Interface to twine."""

    def __init__(self, process=None):
        self.process = process or Process()

    @chdir
    def run_register(self, directory, distfiles, location, quiet=False):
        if not self.process.quiet:
            print(bold('running twine_register'))

        echo = not quiet
        echo2 = True

        serverflags = ['--repository="%(location)s"' % locals()]
        distfiles = [('"%s"' % x) for x in distfiles]

        rc, lines = self._run_twine(
            ['register'] + serverflags + distfiles,
            echo=echo,
            echo2=echo2)

        if rc == 0:
            if not self.process.quiet and quiet:
                print('OK')
            return rc
        err_exit('ERROR: register failed')

    @chdir
    def run_upload(self, directory, distfiles, location, uploadflags, quiet=False):
        if not self.process.quiet:
            print(bold('running twine_upload'))

        echo = not quiet
        echo2 = True

        serverflags = ['--repository="%(location)s"' % locals()]
        distfiles = [('"%s"' % x) for x in distfiles]

        rc, lines = self._run_twine(
            ['upload'] + serverflags + uploadflags + distfiles,
            echo=echo,
            echo2=echo2)

        if rc == 0:
            if not self.process.quiet and quiet:
                print('OK')
            return rc
        err_exit('ERROR: upload failed')

    def _run_twine(self, args, echo=True, echo2=True):
        cmd = 'twine %s' % ' '.join(args)

        # XXX
        print(cmd)
        return 0, []

        try:
            return self.process.popen(cmd, echo=echo, echo2=echo2)
        except KeyboardInterrupt:
            return 1, []

