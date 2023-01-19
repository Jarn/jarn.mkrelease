import sys
import os
import unittest
import tempfile
import shutil
import zipfile
import functools

if sys.version_info[0] >= 3:
    from io import StringIO
else:
    from StringIO import StringIO

from os.path import realpath, join, isdir
from lazy import lazy

from jarn.mkrelease.process import Process
from jarn.mkrelease.chdir import ChdirStack, chdir
from jarn.mkrelease.scm import SCMFactory


class JailSetup(unittest.TestCase):
    """Manage a temporary working directory."""

    dirstack = None
    tempdir = None

    def setUp(self):
        self.addCleanup(self.tearDown)
        self.dirstack = ChdirStack()
        self.tempdir = realpath(self.mkdtemp())
        self.dirstack.push(self.tempdir)

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
        return tempfile.mkdtemp(prefix='jail-')

    def mkfile(self, name, body=''):
        with open(name, 'wt') as file:
            file.write(body)


class SandboxSetup(JailSetup):
    """Put an SCM sandbox into the jail."""

    datadir = realpath('tests')

    source = None
    packagedir = None

    def setUp(self):
        JailSetup.setUp(self)
        package = join(self.datadir, self.source)
        archive = zipfile.ZipFile(package, 'r')
        archive.extractall()
        os.rename(self.source[:-4], 'testpackage')
        self.packagedir = join(self.tempdir, 'testpackage')


class SCMSetup(SandboxSetup):
    """Manage an SCM sandbox."""

    name = None
    clonedir = None

    @lazy
    def scm(self):
        return SCMFactory().get_scm_from_type(self.name)

    def clone(self):
        raise NotImplementedError

    def destroy(self, dir=None):
        if dir is None:
            dir = self.packagedir
        shutil.rmtree(join(dir, '.'+self.name))

    def modify(self, dir):
        appendlines(join(dir, 'setup.py'), ['#foo'])

    def verify(self, dir):
        line = readlines(join(dir, 'setup.py'))[-1]
        self.assertEqual(line, '#foo')

    def delete(self, dir):
        os.remove(join(dir, 'setup.py'))

    def remove(self, dir):
        raise NotImplementedError

    def update(self, dir):
        raise NotImplementedError

    def tag(self, dir, tagid):
        raise NotImplementedError

    def branch(self, dir, branchid):
        raise NotImplementedError


class SubversionSetup(SCMSetup):
    """Manage a Subversion sandbox."""

    name = 'svn'

    def setUp(self):
        SCMSetup.setUp(self)
        self._fake_clone()

    @lazy
    def source(self):
        return 'testrepo.svn18.zip'

    @lazy
    def _fake_source(self):
        return 'testpackage.svn18.zip'

    def clone(self):
        process = Process(quiet=True)
        process.popen('svn checkout file://%s/trunk testclone' % self.packagedir)
        self.clonedir = join(self.tempdir, 'testclone')

    def _fake_clone(self):
        # Fake a checkout, the real thing is too expensive
        process = Process(quiet=True)
        source = self._fake_source
        package = join(self.datadir, source)
        archive = zipfile.ZipFile(package, 'r')
        archive.extractall()
        os.rename(source[:-4], 'testclone')
        self.dirstack.push('testclone')
        url = process.popen('svn info')[1][2][5:]
        process.popen('svn switch --relocate %s file://%s/trunk' % (url, self.packagedir))
        self.dirstack.pop()
        self.clonedir = join(self.tempdir, 'testclone')

    def destroy(self, dir=None):
        if dir is None:
            dir = self.packagedir
        if isdir(join(dir, 'db', 'revs')): # The svn repo
            shutil.rmtree(join(dir, 'db'))
        else:
            for path, dirs, files in os.walk(dir):
                if '.svn' in dirs:
                    shutil.rmtree(join(path, '.svn'))
                    dirs.remove('.svn')

    @chdir
    def modifyprop(self, dir):
        process = Process(quiet=True)
        process.popen('svn propset format "text/x-python" setup.py')

    @chdir
    def remove(self, dir):
        process = Process(quiet=True)
        process.popen('svn remove setup.py')

    @chdir
    def update(self, dir):
        process = Process(quiet=True)
        process.popen('svn update')

    def tag(self, dir, tagid):
        process = Process(quiet=True)
        process.popen('svn cp -m"Tag" file://%s/trunk %s' % (self.packagedir, tagid))
        process.popen('svn co %s testtag' % tagid)
        self.tagdir = join(self.tempdir, 'testtag')

    def branch(self, dir, branchid):
        process = Process(quiet=True)
        process.popen('svn cp -m"Branch" file://%s/trunk %s' % (self.packagedir, branchid))
        process.popen('svn co %s testbranch' % branchid)
        self.branchdir = join(self.tempdir, 'testbranch')


class MercurialSetup(SCMSetup):
    """Manage a Mercurial sandbox."""

    name = 'hg'
    source = 'testpackage.hg.zip'

    def clone(self):
        process = Process(quiet=True)
        process.popen('hg clone testpackage testclone')
        self.clonedir = join(self.tempdir, 'testclone')

    @chdir
    def remove(self, dir):
        process = Process(quiet=True)
        process.popen('hg remove setup.py')

    @chdir
    def update(self, dir):
        process = Process(quiet=True)
        process.popen('hg update')

    @chdir
    def tag(self, dir, tagid):
        process = Process(quiet=True)
        process.popen('hg tag %s' % tagid)
        process.popen('hg update %s' % tagid)

    @chdir
    def branch(self, dir, branchid):
        process = Process(quiet=True)
        process.popen('hg branch %s' % branchid)


class GitSetup(SCMSetup):
    """Manage a Git sandbox."""

    name = 'git'
    source = 'testpackage.git.zip'

    def setUp(self):
        SCMSetup.setUp(self)
        process = Process(quiet=True)
        self.dirstack.push('testpackage')
        process.popen('git config user.name "Your Name"')
        process.popen('git config user.email "you@example.com"')
        self.dirstack.pop()

    def clone(self):
        process = Process(quiet=True)
        process.popen('git clone testpackage testclone')
        self.clonedir = join(self.tempdir, 'testclone')
        # Park the server on a branch
        self.dirstack.push('testpackage')
        process.popen('git checkout parking')
        self.dirstack.pop()
        # Make sure the clone is on master
        self.dirstack.push('testclone')
        process.popen('git checkout master')
        process.popen('git config user.name "Your Name"')
        process.popen('git config user.email "you@example.com"')
        self.dirstack.pop()

    @chdir
    def remove(self, dir):
        process = Process(quiet=True)
        process.popen('git rm setup.py')

    @chdir
    def update(self, dir):
        process = Process(quiet=True)
        process.popen('git checkout master')

    @chdir
    def tag(self, dir, tagid):
        process = Process(quiet=True)
        process.popen('git tag %s' % tagid)
        process.popen('git checkout %s' % tagid)

    @chdir
    def branch(self, dir, branchid):
        process = Process(quiet=True)
        process.popen('git branch %s' % branchid)
        process.popen('git checkout %s' % branchid)


class MockProcessError(Exception):
    """Raised by MockProcess."""


class MockProcess(Process):
    """A Process we can tell what to return by

    - passing rc and lines, or
    - passing a function called as ``func(cmd)`` which returns
      rc and lines.
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
                raise MockProcessError('Unhandled command: %s' % cmd)
        return self.rc, self.lines


def quiet(func):
    """Decorator swallowing stdout and stderr output.
    """
    def wrapper(self, *args, **kw):
        saved = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = StringIO()
        try:
            return func(self, *args, **kw)
        finally:
            sys.stdout, sys.stderr = saved

    return functools.wraps(func)(wrapper)


def readlines(filename):
    """Read lines from file 'filename'.

    Lines are not newline terminated.
    """
    with open(filename, 'rt') as file:
        return file.read().strip().split('\n')


def appendlines(filename, lines):
    """Append 'lines' to file 'filename'.
    """
    with open(filename, 'at') as file:
        for line in lines:
            file.write(line+'\n')


class setenv(object):
    """Context manager to set an environment variable."""

    def __init__(self, name, val):
        self._name = name
        self._val = val
        self._saved = None

    def __enter__(self):
        self._saved = os.environ.get(self._name, None)
        os.environ[self._name] = self._val

    def __exit__(self, *ignored):
        if self._saved is not None:
            os.environ[self._name] = self._saved
        else:
            del os.environ[self._name]


class delenv(object):
    """Context manager to delete an environment variable."""

    def __init__(self, name):
        self._name = name
        self._saved = None

    def __enter__(self):
        self._saved = os.environ.get(self._name, None)
        if self._saved is not None:
            del os.environ[self._name]

    def __exit__(self, *ignored):
        if self._saved is not None:
            os.environ[self._name] = self._saved

