import os
import tee


class Process(object):
    """Process related functions using the tee module (mostly)."""

    def __init__(self, quiet=False, env=None):
        self.quiet = quiet
        self.env = env

    def popen(self, cmd, echo=True, echo2=True):
        if self.quiet:
            echo = echo2 = False
        return tee.popen(cmd, echo, echo2, env=self.env)

    def pipe(self, cmd):
        rc, lines = self.popen(cmd, echo=False)
        if rc == 0 and lines:
            return lines[0]
        return ''

    def system(self, cmd):
        rc, lines = self.popen(cmd, echo=tee.NotEmpty())
        return rc

    def os_system(self, cmd):
        if self.quiet:
            cmd = cmd + ' >%s 2>&1' % os.devnull
        if self.env:
            cmd = ''.join('%s=%s ' % (k, v) for k, v in self.env.items()) + cmd
        return os.system(cmd)

