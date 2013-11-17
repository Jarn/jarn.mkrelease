import sys
import locale
import functools

preferrederrors = 'replace'


def memoize(func):
    """Cache forever."""
    cache = {}
    def memoizer():
        if 0 not in cache:
            cache[0] = func()
        return cache[0]
    return functools.wraps(func)(memoizer)


@memoize
def getpreferredencoding():
    """Return preferred encoding for text I/O."""
    encoding = locale.getpreferredencoding(False)
    if sys.platform == 'darwin' and encoding.startswith('mac-'):
        # Upgrade ancient MacOS encodings in Python < 2.7
        encoding = 'utf-8'
    return encoding


def getpreferrederrors():
    """Return preferred error handler (currently 'replace')."""
    return preferrederrors


def getinputencoding(stream=None):
    """Return preferred encoding for reading from ``stream``.

    ``stream`` defaults to sys.stdin.
    """
    if stream is None:
        stream = sys.stdin
    encoding = stream.encoding
    if not encoding:
        encoding = getpreferredencoding()
    return encoding


def getoutputencoding(stream=None):
    """Return preferred encoding for writing to ``stream``.

    ``stream`` defaults to sys.stdout.
    """
    if stream is None:
        stream = sys.stdout
    encoding = stream.encoding
    if not encoding:
        encoding = getpreferredencoding()
    return encoding


def decode(string, encoding=None, errors=None):
    """Decode from specified encoding.

    ``encoding`` defaults to the preferred encoding.
    ``errors`` defaults to the preferred error handler.
    """
    if encoding is None:
        encoding = getpreferredencoding()
    if errors is None:
        errors = getpreferrederrors()
    return string.decode(encoding, errors)


def encode(string, encoding=None, errors=None):
    """Encode to specified encoding.

    ``encoding`` defaults to the preferred encoding.
    ``errors`` defaults to the preferred error handler.
    """
    if encoding is None:
        encoding = getpreferredencoding()
    if errors is None:
        errors = getpreferrederrors()
    return string.encode(encoding, errors)

