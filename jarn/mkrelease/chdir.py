import os
import functools


class ChdirStack(object):
    """Stack of current working directories."""

    def __init__(self):
        self.stack = []

    def __len__(self):
        return len(self.stack)

    def push(self, dir):
        """Push cwd on stack and change to 'dir'.
        """
        self.stack.append(os.getcwd())
        os.chdir(dir or os.getcwd())

    def pop(self):
        """Pop dir off stack and change to it.
        """
        if len(self.stack):
            os.chdir(self.stack.pop())


def chdir(method):
    """Decorator executing method in directory 'dir'.
    """
    def wrapper(self, dir, *args, **kw):
        dirstack = ChdirStack()
        dirstack.push(dir)
        try:
            return method(self, dir, *args, **kw)
        finally:
            dirstack.pop()

    return functools.wraps(method)(wrapper)

