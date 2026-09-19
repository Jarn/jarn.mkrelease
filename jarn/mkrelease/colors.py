import os

from termcolor import colored


def color(fg=None, **kwargs):
    def paint(string):
        if os.environ.get('JARN_NO_COLOR') == '1':
            return string
        return colored(string, fg, **kwargs)
    return paint


bold = color(attrs=['bold'])
blue = color('blue', attrs=['bold'])
green = color('green', attrs=['bold'])
red = color('red', attrs=['bold'])
