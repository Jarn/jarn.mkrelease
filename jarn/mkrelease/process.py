import os
import tee


class Process(object):
    """Process related functions using the tee module."""

    def __init__(self, quiet=False, env=None):
        self.quiet = quiet
        self.env = env

    def popen(self, cmd, echo=True, echo2=True):
        # env *replaces* os.environ
        if self.quiet:
            echo = echo2 = False
        return tee.popen(cmd, echo, echo2, env=self.env)

    def pipe(self, cmd):
        rc, lines = self.popen(cmd, echo=False)
        if rc == 0 and lines:
            return lines[0]
        return ''

    def system(self, cmd):
        rc, lines = self.popen(cmd)
        return rc

    def os_system(self, cmd):
        # env *updates* os.environ
        if self.quiet:
            cmd = cmd + ' >%s 2>&1' % os.devnull
        if self.env:
            cmd = ''.join('export %s="%s"\n' % (k, v) for k, v in self.env.iteritems()) + cmd
        return os.system(cmd)

