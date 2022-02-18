import os
import functools
import blessed


def color(func):
    functools.wraps(func)
    def wrapper(string):
        if os.environ.get('JARN_NO_COLOR') == '1':
            return string
        return func(string)
    return wrapper


term = blessed.Terminal()

bold = color(term.bold)
blue = color(term.bold_blue)
green = color(term.bold_green)
red = color(term.bold_red)

