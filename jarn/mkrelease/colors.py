import sys


def plain(string):
    return '\033[0m'+string if sys.stdout.isatty() else string


def bold(string):
    return '\033[0;1m'+string+'\033[0m' if sys.stdout.isatty() else string


def red(string):
    return '\033[0;31;1m'+string+'\033[0m' if sys.stdout.isatty() else string


def green(string):
    return '\033[0;32;1m'+string+'\033[0m' if sys.stdout.isatty() else string


def yellow(string):
    return '\033[0;33;1m'+string+'\033[0m' if sys.stdout.isatty() else string


def blue(string):
    return '\033[0;34;1m'+string+'\033[0m' if sys.stdout.isatty() else string

