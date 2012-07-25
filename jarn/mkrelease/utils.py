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
