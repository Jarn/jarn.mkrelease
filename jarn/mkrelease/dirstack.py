import os


class DirStack(object):
    """Manage a stack of current working directories."""

    def __init__(self):
        self.stack = []

    def __len__(self):
        return len(self.stack)

    def push(self, dir):
        """Push cwd on stack and chdir to 'dir'.
        """
        self.stack.append(os.getcwd())
        os.chdir(dir)

    def pop(self):
        """Pop dir off stack and chdir to it.
        """
        if len(self):
            os.chdir(self.stack.pop())


class WithDirStack(object):
    """Inherit from this to gain 'pushdir' and 'popdir' methods."""

    def __init__(self):
        self.dirstack = DirStack()

    def pushdir(self, dir):
        self.dirstack.push(dir)

    def popdir(self):
        self.dirstack.pop()


def chdir(func):
    """Decorator executing 'func' in directory 'dir'.
    """
    def wrapped_func(self, dir, *args, **kw):
        assert isinstance(self, WithDirStack)

        self.pushdir(dir)
        try:
            return func(self, dir, *args, **kw)
        finally:
            self.popdir()

    wrapped_func.__name__ = func.__name__
    wrapped_func.__dict__ = func.__dict__
    wrapped_func.__doc__ = func.__doc__
    return wrapped_func

