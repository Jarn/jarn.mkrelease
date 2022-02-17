from __future__ import absolute_import

import sys
import threading

from subprocess import Popen, PIPE
from .utils import decode


__all__ = ['On', 'Off', 'NotEmpty', 'Equals', 'Contains',
           'StartsWith', 'EndsWith', 'Before', 'NotAfter',
           'After', 'NotBefore', 'Not', 'And', 'Or']


def tee(process, filter):
    """Read lines from process.stdout and echo them to sys.stdout.

    Returns a list of lines read. Lines are not newline terminated.

    The 'filter' is a callable which is invoked for every line,
    receiving the line as argument. If the filter returns True, the
    line is echoed to sys.stdout.
    """
    lines = []

    while True:
        try:
            line = process.stdout.readline()
            if line:
                if sys.version_info[0] >= 3:
                    line = decode(line)
                stripped_line = line.rstrip()
                if filter(stripped_line):
                    sys.stdout.write(line)
                lines.append(stripped_line)
            elif process.poll() is not None:
                process.stdout.close()
                break
        except KeyboardInterrupt:
            process.returncode = 1
            raise
    return lines


def tee2(process, filter):
    """Read lines from process.stderr and echo them to sys.stderr.

    The 'filter' is a callable which is invoked for every line,
    receiving the line as argument. If the filter returns True, the
    line is echoed to sys.stderr.
    """
    while True:
        line = process.stderr.readline()
        if line:
            if sys.version_info[0] >= 3:
                line = decode(line)
            stripped_line = line.rstrip()
            if filter(stripped_line):
                sys.stderr.write(line)
        elif process.returncode is not None:
            process.stderr.close()
            break


class background_thread(object):
    """Context manager to start and stop a background thread."""

    def __init__(self, target, args):
        self.target = target
        self.args = args

    def __enter__(self):
        self._t = threading.Thread(target=self.target, args=self.args)
        self._t.start()
        return self._t

    def __exit__(self, *ignored):
        self._t.join()


def run(args, echo=True, echo2=True, shell=False, cwd=None, env=None):
    """Run 'args' and return a two-tuple of exit code and lines read.

    If 'echo' is True, the stdout stream is echoed to sys.stdout.
    If 'echo2' is True, the stderr stream is echoed to sys.stderr.

    The 'echo' and 'echo2' arguments may be callables, in which
    case they are used as tee filters.

    If 'shell' is True, args are executed via the shell.
    The 'cwd' argument causes the child process to be executed in cwd.
    The 'env' argument allows to pass a dict replacing os.environ.
    """
    if not callable(echo):
        echo = On() if echo else Off()

    if not callable(echo2):
        echo2 = On() if echo2 else Off()

    process = Popen(
        args,
        stdout=PIPE,
        stderr=PIPE,
        shell=shell,
        cwd=cwd,
        env=env
    )

    with background_thread(tee2, (process, echo2)):
        lines = tee(process, echo)

    return process.returncode, lines


def system(args, echo=True, echo2=True, shell=False, cwd=None, env=None):
    """Run 'args' and return a two-tuple of exit code and empty list.

    Does not capture stdout and stderr.
    'echo' and 'echo2' have no effect.

    If 'shell' is True, args are executed via the shell.
    The 'cwd' argument causes the child process to be executed in cwd.
    The 'env' argument allows to pass a dict replacing os.environ.
    """
    process = Popen(
        args,
        stdout=None,
        stderr=None,
        shell=shell,
        cwd=cwd,
        env=env
    )

    process.communicate()

    return process.returncode, []


class On(object):
    """A tee filter printing all lines."""

    def __init__(self):
        pass

    def __call__(self, line):
        return True


class Off(object):
    """A tee filter suppressing all lines."""

    def __init__(self):
        pass

    def __call__(self, line):
        return False


class NotEmpty(object):
    """A tee filter suppressing empty lines."""

    def __init__(self):
        pass

    def __call__(self, line):
        return not not line


class Equals(object):
    """A tee filter printing lines matching one of 'patterns'."""

    def __init__(self, *patterns):
        self.patterns = patterns

    def __call__(self, line):
        return line in self.patterns


class Contains(object):
    """A tee filter printing lines containing one of 'patterns'."""

    def __init__(self, *patterns):
        self.patterns = patterns

    def __call__(self, line):
        for pattern in self.patterns:
            if pattern in line:
                return True
        return False


class StartsWith(object):
    """A tee filter printing lines starting with one of 'patterns'."""

    def __init__(self, *patterns):
        self.patterns = patterns

    def __call__(self, line):
        return line.startswith(self.patterns)


class EndsWith(object):
    """A tee filter printing lines ending with one of 'patterns'."""

    def __init__(self, *patterns):
        self.patterns = patterns

    def __call__(self, line):
        return line.endswith(self.patterns)


class Before(object):
    """A tee filter printing lines before 'stopline'."""

    def __init__(self, stopline):
        self.echo = True
        self.stopline = stopline

    def __call__(self, line):
        if self.echo:
            if line == self.stopline:
                self.echo = False
        return self.echo


class NotAfter(object):
    """A tee filter suppressing lines after 'stopline'."""

    def __init__(self, stopline):
        self.echo = True
        self.stopline = stopline

    def __call__(self, line):
        if self.echo:
            if line == self.stopline:
                self.echo = False
                return True
        return self.echo


class After(object):
    """A tee filter printing lines after 'startline'."""

    def __init__(self, startline):
        self.echo = False
        self.startline = startline

    def __call__(self, line):
        if not self.echo:
            if line == self.startline:
                self.echo = True
                return False
        return self.echo


class NotBefore(object):
    """A tee filter suppressing lines before 'startline'."""

    def __init__(self, startline):
        self.echo = False
        self.startline = startline

    def __call__(self, line):
        if not self.echo:
            if line == self.startline:
                self.echo = True
        return self.echo


class Not(object):
    """Negate a tee filter."""

    def __init__(self, filter):
        self.filter = filter

    def __call__(self, line):
        return not self.filter(line)


class And(object):
    """Apply filter1 and filter2."""

    def __init__(self, filter1, filter2):
        self.filter1 = filter1
        self.filter2 = filter2

    def __call__(self, line):
        return self.filter1(line) and self.filter2(line)


class Or(object):
    """Apply filter1 or filter2."""

    def __init__(self, filter1, filter2):
        self.filter1 = filter1
        self.filter2 = filter2

    def __call__(self, line):
        return self.filter1(line) or self.filter2(line)

