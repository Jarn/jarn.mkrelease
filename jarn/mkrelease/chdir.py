import os


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
    def wrapped_method(self, dir, *args, **kw):
        dirstack = ChdirStack()
        dirstack.push(dir)
        try:
            return method(self, dir, *args, **kw)
        finally:
            dirstack.pop()

    wrapped_method.__name__ = method.__name__
    wrapped_method.__module__ = method.__module__
    wrapped_method.__doc__ = method.__doc__
    wrapped_method.__dict__.update(method.__dict__)
    return wrapped_method

