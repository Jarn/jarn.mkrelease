import sys

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
        if not line and process.poll() is not None:
            break
        stripped_line = line.rstrip()
        if filter(stripped_line):
            sys.stdout.write(line)
        lines.append(stripped_line)
    return lines


def popen(cmd, echo=True, echo2=True, env=None):
    """Run 'cmd' and return a two-tuple of exit code and lines read.

    If 'echo' is True, the stdout stream is echoed to sys.stdout.
    If 'echo2' is True, the stderr stream is echoed to sys.stderr.

    The 'echo' argument may be a callable, in which case it is used
    as a tee filter.

    The optional 'env' argument allows to pass an os.environ-like dict.
    """
    filter = echo
    if not callable(echo):
        filter = echo and On() or Off()
    stream2 = None
    if not echo2:
        stream2 = PIPE
    process = Popen(
        cmd,
        shell=True,
        stdout=PIPE,
        stderr=stream2,
        env=env
    )
    process.poll() # Allow process to start up
    lines = tee(process, filter)
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
        return bool(line)


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


class StartsWith(object):
    """A tee filter printing lines starting with one
    of the patterns."""

    def __init__(self, *patterns):
        self.patterns = patterns

    def __call__(self, line):
        for pattern in self.patterns:
            if line.startswith(pattern):
                return True
        return False


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

