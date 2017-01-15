from __future__ import print_function

import sys


def msg_exit(msg, rc=0):
    """Print msg to stdout and exit with rc.
    """
    print(msg)
    sys.exit(rc)


def err_exit(msg, rc=1):
    """Print msg to stderr and exit with rc.
    """
    print(msg, file=sys.stderr)
    sys.exit(rc)


def warn(msg):
    """Print a warning message to stderr.
    """
    print('WARNING:', msg, file=sys.stderr)

