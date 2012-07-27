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


def contentdecode(string, strict=True):
    """Decode from the preferred charset."""
    return string.decode(locale.getpreferredencoding(False),
        'strict' if strict else errors)


def contentencode(string, strict=True):
    """Encode to the preferred charset."""
    return string.encode(locale.getpreferredencoding(False),
        'strict' if strict else errors)

