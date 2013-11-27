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

from os.path import realpath, join, dirname, isdir
from lazy import lazy

from jarn.mkrelease.process import Process
from jarn.mkrelease.chdir import ChdirStack, chdir
from jarn.mkrelease.scm import SCMFactory


class JailSetup(unittest.TestCase):
    """Manage a temporary working directory."""

    dirstack = None
    tempdir = None

    def setUp(self):
        self.dirstack = ChdirStack()
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

    def mkfile(self, name, body=''):
        with open(name, 'wt') as file:
            file.write(body)


class SandboxSetup(JailSetup):
    """Put an SCM sandbox into the jail."""

    source = None
    packagedir = None

    def setUp(self):
        JailSetup.setUp(self)
        try:
            package = join(dirname(__file__), 'tests', self.source)
            archive = zipfile.ZipFile(package, 'r')
            archive.extractall()
            os.rename(self.source[:-4], 'testpackage')
            self.packagedir = join(self.tempdir, 'testpackage')
        except:
            self.cleanUp()
            raise


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
        try:
            self._fake_clone()
        except:
            self.cleanUp()
            raise

    @lazy
    def source(self):
        if self.scm.version_info[:2] >= (1, 8):
            return 'testrepo.svn18.zip'
        elif self.scm.version_info[:2] >= (1, 7):
            return 'testrepo.svn17.zip'
        else:
            return 'testrepo.svn16.zip'

    @lazy
    def _fake_source(self):
        if self.scm.version_info[:2] >= (1, 8):
            return 'testpackage.svn18.zip'
        elif self.scm.version_info[:2] >= (1, 7):
            return 'testpackage.svn17.zip'
        else:
            return 'testpackage.svn16.zip'

    def clone(self):
        process = Process(quiet=True)
        process.system('svn checkout file://%s/trunk testclone' % self.packagedir)
        self.clonedir = join(self.tempdir, 'testclone')

    def _fake_clone(self):
        # Fake a checkout, the real thing is too expensive
        process = Process(quiet=True)
        source = self._fake_source
        package = join(dirname(__file__), 'tests', source)
        archive = zipfile.ZipFile(package, 'r')
        archive.extractall()
        os.rename(source[:-4], 'testclone')
        self.dirstack.push('testclone')
        if self.scm.version_info[:2] >= (1, 7):
            url = process.popen('svn info')[1][2][5:]
        else:
            url = process.popen('svn info')[1][1][5:]
        process.system('svn switch --relocate %s file://%s/trunk' % (url, self.packagedir))
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
        if self.scm.version_info[:2] >= (1, 8):
            process.system('svn propset format "text/x-python" setup.py')
        else:
            process.system('svn propset svn:format "text/x-python" setup.py')

    @chdir
    def remove(self, dir):
        process = Process(quiet=True)
        process.system('svn remove setup.py')

    @chdir
    def update(self, dir):
        process = Process(quiet=True)
        process.system('svn update')

    def tag(self, dir, tagid):
        process = Process(quiet=True)
        process.system('svn cp -m"Tag" file://%s/trunk %s' % (self.packagedir, tagid))
        process.system('svn co %s testtag' % tagid)
        self.tagdir = join(self.tempdir, 'testtag')

    def branch(self, dir, branchid):
        process = Process(quiet=True)
        process.system('svn cp -m"Branch" file://%s/trunk %s' % (self.packagedir, branchid))
        process.system('svn co %s testbranch' % branchid)
        self.branchdir = join(self.tempdir, 'testbranch')


class MercurialSetup(SCMSetup):
    """Manage a Mercurial sandbox."""

    name = 'hg'
    source = 'testpackage.hg.zip'

    def clone(self):
        process = Process(quiet=True)
        process.system('hg clone testpackage testclone')
        self.clonedir = join(self.tempdir, 'testclone')

    @chdir
    def remove(self, dir):
        process = Process(quiet=True)
        process.system('hg remove setup.py')

    @chdir
    def update(self, dir):
        process = Process(quiet=True)
        process.system('hg update')

    @chdir
    def tag(self, dir, tagid):
        process = Process(quiet=True)
        process.system('hg tag %s' % tagid)
        process.system('hg update %s' % tagid)

    @chdir
    def branch(self, dir, branchid):
        process = Process(quiet=True)
        process.system('hg branch %s' % branchid)


class GitSetup(SCMSetup):
    """Manage a Git sandbox."""

    name = 'git'
    source = 'testpackage.git.zip'

    def clone(self):
        process = Process(quiet=True)
        process.system('git clone testpackage testclone')
        self.clonedir = join(self.tempdir, 'testclone')
        # Park the server on a branch
        self.dirstack.push('testpackage')
        process.system('git checkout parking')
        self.dirstack.pop()
        # Make sure the clone is on master
        self.dirstack.push('testclone')
        process.system('git checkout master')
        self.dirstack.pop()

    @chdir
    def remove(self, dir):
        process = Process(quiet=True)
        process.system('git rm setup.py')

    @chdir
    def update(self, dir):
        process = Process(quiet=True)
        process.system('git checkout master')

    @chdir
    def tag(self, dir, tagid):
        process = Process(quiet=True)
        process.system('git tag %s' % tagid)
        process.system('git checkout %s' % tagid)

    @chdir
    def branch(self, dir, branchid):
        process = Process(quiet=True)
        process.system('git branch %s' % branchid)
        process.system('git checkout %s' % branchid)


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

    def os_system(self, cmd):
        if self.func is not None:
            rc_lines = self.func(cmd)
            if rc_lines is not None:
                return rc_lines[0]
            else:
                raise MockProcessError('Unhandled command: %s' % cmd)
        return self.rc


def quiet(func):
    """Decorator swallowing stdout and stderr output.
    """
    def wrapper(*args, **kw):
        saved = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = StringIO()
        try:
            return func(*args, **kw)
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

