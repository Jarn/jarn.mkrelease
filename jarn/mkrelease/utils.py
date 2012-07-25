import sys
import locale

if sys.version_info[0] >= 3:
    errors = 'surrogateescape'
else:
    errors = 'replace'


def decode(string):
    """Decode from the charset of the current locale."""
    return string.decode(locale.getlocale()[1], errors)


def encode(string):
    """Encode to the charset of the current locale."""
    return string.encode(locale.getlocale()[1], errors)


def char(int):
    """Create a one-character byte string from the ordinal ``int``."""
    if sys.version_info[0] >= 3:
        return bytes((int,))
    else:
        return chr(int)


def b(string, encoding='utf-8'):
    """Used instead of b'' literals to stay Python 2.5 compatible.

    ``encoding`` should match the encoding of the source file.
    """
    if isinstance(string, unicode):
        return string.encode(encoding)
    return string

