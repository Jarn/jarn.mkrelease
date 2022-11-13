import os
import functools
import blessed


def color(func):
    assignments = functools.WRAPPER_ASSIGNMENTS
    if not hasattr(func, '__name__'):
        assignments = [x for x in assignments if x != '__name__']

    @functools.wraps(func, assignments)
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

