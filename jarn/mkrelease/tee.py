import sys
import threading

from subprocess import Popen, PIPE


def tee(process, filter):
    """Read lines from process.stdout and echo them to sys.stdout.

    Returns a list of lines read. Lines are not newline terminated.

    The 'filter' is a callable which is invoked for every line,
    receiving the line as argument. If the filter returns True, the
    line is echoed to sys.stdout.
    """
    # We simply use readline here, more fancy IPC is not warranted
    # in the context of this package.
    lines = []
    while True:
        line = process.stdout.readline()
        if line:
            stripped_line = line.rstrip()
            if filter(stripped_line):
                sys.stdout.write(line)
            lines.append(stripped_line)
        elif process.poll() is not None:
            break
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
            stripped_line = line.rstrip()
            if filter(stripped_line):
                sys.stderr.write(line)
        elif process.poll() is not None:
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


def popen(cmd, echo=True, echo2=True, env=None):
    """Run 'cmd' and return a two-tuple of exit code and lines read.

    If 'echo' is True, the stdout stream is echoed to sys.stdout.
    If 'echo2' is True, the stderr stream is echoed to sys.stderr.

    The 'echo' and 'echo2' arguments may also be callables, in which
    case they are used as tee filters.

    The 'env' argument allows to pass a dict replacing os.environ.
    """
    if not callable(echo):
        echo = On() if echo else Off()

    if not callable(echo2):
        echo2 = On() if echo2 else Off()

    process = Popen(
        cmd,
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
        env=env
    )

    with background_thread(tee2, (process, echo2)):
        lines = tee(process, echo)

    return process.returncode, lines


class On(object):
    """A tee filter printing all lines."""

    def __call__(self, line):
        return True


class Off(object):
    """A tee filter suppressing all lines."""

    def __call__(self, line):
        return False


class NotEmpty(object):
    """A tee filter suppressing empty lines."""

    def __call__(self, line):
        return not not line


class Equals(object):
    """A tee filter printing lines matching one of 'patterns'."""

    def __init__(self, *patterns):
        self.patterns = patterns

    def __call__(self, line):
        for pattern in self.patterns:
            if line == pattern:
                return True
        return False


class StartsWith(object):
    """A tee filter printing lines starting with one of 'patterns'."""

    def __init__(self, *patterns):
        self.patterns = patterns

    def __call__(self, line):
        for pattern in self.patterns:
            if line.startswith(pattern):
                return True
        return False


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

