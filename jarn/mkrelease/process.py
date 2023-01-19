from __future__ import absolute_import

import os

from .tee import run
from .exit import trace

catch_keyboard_interrupts = True


class Process(object):
    """Process related functions using the tee module."""

    rc_keyboard_interrupt = 54321

    def __init__(self, quiet=False, env=None, runner=run):
        self.quiet = quiet
        self.env = env
        self.runner = runner

    def popen(self, cmd, echo=True, echo2=True):
        # env *replaces* os.environ
        trace(cmd)
        if self.quiet:
            echo = echo2 = False
        try:
            return self.runner(cmd, echo, echo2, shell=True, env=self.env)
        except KeyboardInterrupt:
            if catch_keyboard_interrupts:
                return self.rc_keyboard_interrupt, []
            raise

