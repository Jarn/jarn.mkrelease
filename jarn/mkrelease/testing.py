import sys
import os
import unittest
import tempfile
import shutil
import StringIO

from os.path import realpath, join, dirname, isdir

from jarn.mkrelease.process import Process
from jarn.mkrelease.dirstack import DirStack


class JailSetup(unittest.TestCase):
    """Manage a temporary working directory."""

    dirstack = None
    tempdir = None

    def setUp(self):
        self.dirstack = DirStack()
        try:
            self.tempdir = realpath(self.mkdtemp())
            self.dirstack.push(self.tempdir)
        except:
            self.cleanUp()
            raise

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        if self.dirstack is not None:
            while self.dirstack:
                self.dirstack.pop()
        if self.tempdir is not None:
            if isdir(self.tempdir):
                shutil.rmtree(self.tempdir)

    def mkdtemp(self):
        return tempfile.mkdtemp()


class PackageSetup(JailSetup):
    """Make sure the jail contains a testpackage."""

    name = ''
    source = None
    packagedir = None
    clonedir = None

    def setUp(self):
        JailSetup.setUp(self)
        try:
            package = join(dirname(__file__), 'tests', self.source)
            self.packagedir = join(self.tempdir, 'testpackage')
            shutil.copytree(package, self.packagedir)
        except:
            self.cleanUp()
            raise

    def clone(self):
        pass

    def destroy(self, dir=None, name=None):
        if dir is None:
            dir = self.packagedir
        if name is None:
            name = self.name
        if name:
            shutil.rmtree(join(dir, '.'+name))

    def modify(self, dir):
        appendlines(join(dir, 'setup.py'), ['#foo'])

    def verify(self, dir):
        line = readlines(join(dir, 'setup.py'))[-1]
        self.assertEqual(line, '#foo')


class SubversionSetup(PackageSetup):
    """Set up a Subversion sandbox."""

    name = 'svn'
    source = 'testpackage.svn'


class MercurialSetup(PackageSetup):
    """Set up a Mercurial sandbox."""

    name = 'hg'
    source = 'testpackage.hg'

    def clone(self):
        process = Process(quiet=True)
        process.system('hg clone testpackage testclone')
        self.clonedir = join(self.tempdir, 'testclone')


class GitSetup(PackageSetup):
    """Set up a Git sandbox."""

    name = 'git'
    source = 'testpackage.git'

    def clone(self):
        process = Process(quiet=True)
        process.system('git clone testpackage testclone')
        self.clonedir = join(self.tempdir, 'testclone')
        # Park the server on a branch because "Updating the currently checked
        # out branch may cause confusion..."
        self.dirstack.push('testpackage')
        process.system('git checkout -b parking')
        self.dirstack.pop()


class TestProcessError(Exception):
    """Raised by TestProcess."""


class TestProcess(Process):
    """A Process we can tell what to return by

    - passing rc and lines, or
    - passing a function that returns rc and lines depending on cmd.
    """

    def __init__(self, rc=None, lines=None, func=None):
        Process.__init__(self, quiet=True)
        self.rc = rc or 0
        self.lines = lines or []
        self.func = func

    def popen(self, cmd, echo=True, echo2=True):
        if self.func is not None:
            rc_lines = self.func(cmd)
            if rc_lines is not None:
                return rc_lines
            else:
                raise TestProcessError('Unhandled command: %s' % cmd)
        return self.rc, self.lines

    def os_system(self, cmd):
        if self.func is not None:
            rc_lines = self.func(cmd)
            if rc_lines is not None:
                return rc_lines[0]
            else:
                raise TestProcessError('Unhandled command: %s' % cmd)
        return self.rc


def quiet(func):
    """Decorator swallowing stdout and stderr output.
    """
    def wrapped_func(*args, **kw):
        saved = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = StringIO.StringIO()
        try:
            return func(*args, **kw)
        finally:
            sys.stdout, sys.stderr = saved

    wrapped_func.__name__ = func.__name__
    wrapped_func.__dict__ = func.__dict__
    wrapped_func.__doc__ = func.__doc__
    return wrapped_func


def readlines(filename):
    """Read lines from file 'filename'.

    Lines are not newline terminated.
    """
    f = open(filename, 'rb')
    try:
        return f.read().rstrip().replace('\r', '\n').split('\n')
    finally:
        f.close()


def appendlines(filename, lines):
    """Append 'lines' to file 'filename'.
    """
    f = open(filename, 'at')
    try:
        for line in lines:
            f.write(line+'\n')
    finally:
        f.close()

