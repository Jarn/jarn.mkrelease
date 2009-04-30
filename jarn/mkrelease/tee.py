from subprocess import Popen, PIPE
from sys import stdout


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
        lines.append(stripped_line)
        if filter(stripped_line):
            stdout.write(line)
    return lines


def popen(cmd, echo=True, echo2=True):
    """Run cmd and return a two-tuple of exit code and lines read.

    If echo is True, the stdout stream is echoed to sys.stdout.
    If echo2 is True, the stderr stream is echoed to sys.stderr.

    The echo argument may be a callable, in which case it is used
    as a tee filter.
    """
    stream2 = not echo2 and PIPE or None
    process = Popen(cmd, shell=True, stdout=PIPE, stderr=stream2)
    filter = echo
    if not callable(echo):
        filter = echo and On() or Off()
    lines = tee(process, filter)
    return process.returncode, lines


def system(cmd):
    """Run cmd and return its exit code.
    """
    rc, lines = popen(cmd)
    return rc


def pipe(cmd):
    """Run cmd and return the first line of its output.

    Returns empty string if cmd fails or does not produce
    any output.
    """
    rc, lines = popen(cmd, echo=False)
    if rc == 0 and lines:
        return lines[0]
    return ''


class On(object):
    """A tee filter printing all lines."""

    def __call__(self, line):
        return True


class Off(object):
    """A tee filter suppressing all lines."""

    def __call__(self, line):
        return False


class NotEmpty(object):
    """A tee filter supressing empty lines."""

    def __call__(self, line):
        return bool(line)


class NotBefore(object):
    """A tee filter supressing output before 'startline'."""

    def __init__(self, startline):
        self.echo = False
        self.startline = startline

    def __call__(self, line):
        if not self.echo:
            if line == self.startline:
                self.echo = True
        return self.echo


class NotAfter(object):
    """A tee filter supressing output after 'stopline'."""

    def __init__(self, stopline):
        self.echo = True
        self.stopline = stopline

    def __call__(self, line):
        echo = self.echo
        if self.echo:
            if line == self.stopline:
                self.echo = False
        return echo

