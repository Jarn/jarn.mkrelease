import os
import tee
import pkg_resources

from os.path import abspath, join, isfile

from python import Python
from process import Process
from configparser import ConfigParser
from chdir import chdir
from exit import err_exit, warn


class Setuptools(object):
    """Interface to setuptools."""

    def __init__(self, process=None):
        self.process = process or Process(env=self.get_env())
        self.python = Python()

    def get_env(self):
        # Make sure setuptools and its extensions are found if mkrelease
        # has been installed with zc.buildout
        path = []
        for name in ('setuptools', 'setuptools-hg', 'setuptools-git',
                     'setuptools-subversion'):
            try:
                dist = pkg_resources.get_distribution(name)
            except pkg_resources.DistributionNotFound:
                continue
            path.append(dist.location)
        env = os.environ.copy()
        env['PYTHONPATH'] = ':'.join(path)
        env['HG_SETUPTOOLS_FORCE_CMD'] = '1'
        return env

    def is_valid_package(self, dir):
        return isfile(join(dir, 'setup.py'))

    def check_valid_package(self, dir):
        if not self.is_valid_package(dir):
            err_exit('No setup.py found in %(dir)s' % locals())

    @chdir
    def get_package_info(self, dir, develop=False):
        python = self.python
        rc, lines = self.process.popen(
            '"%(python)s" setup.py --name --version' % locals(), echo=False)
        if rc == 0 and len(lines) == 2:
            name, version = lines
            if develop:
                parser = ConfigParser(warn)
                parser.read('setup.cfg')
                version += parser.get('egg_info', 'tag_build', '').strip()
            return name, pkg_resources.safe_version(version)
        err_exit('Bad setup.py')

    @chdir
    def run_egg_info(self, dir, infoflags, ff='', quiet=False):
        if not self.process.quiet:
            print 'running egg_info'

        echo = tee.After('running egg_info')
        if quiet:
            echo = tee.And(echo, tee.StartsWith('running'))

        rc, lines = self._run_setup_py(
            ['egg_info'] + infoflags,
            echo=echo,
            ff=ff)

        if rc == 0:
            filename = self._parse_egg_info_results(lines)
            if filename and isfile(filename):
                return abspath(filename)
        err_exit('egg_info failed')

    @chdir
    def run_dist(self, dir, infoflags, distcmd, distflags, ff='', quiet=False):
        if not self.process.quiet:
            print 'running', distcmd

        echo = tee.After('running %(distcmd)s' % locals())
        if quiet:
            echo = tee.And(echo, tee.StartsWith('running'))

        rc, lines = self._run_setup_py(
            ['egg_info'] + infoflags + [distcmd] + distflags,
            echo=echo,
            ff=ff)

        if rc == 0:
            filename = self._parse_dist_results(lines)
            if filename and isfile(filename):
                return abspath(filename)
        err_exit('%(distcmd)s failed' % locals())

    @chdir
    def run_register(self, dir, infoflags, location, ff='', quiet=False):
        if not self.process.quiet:
            print 'running register'

        echo = tee.After('running register')
        if quiet:
            echo = tee.And(echo, tee.Not(tee.StartsWith('Registering')))

        serverflags = ['--repository="%s"' % location]

        rc, lines = self._run_setup_py(
            ['egg_info'] + infoflags + ['register'] + serverflags,
            echo=echo,
            ff=ff)

        if rc == 0:
            if self._parse_register_results(lines):
                return rc
        err_exit('register failed')

    @chdir
    def run_upload(self, dir, infoflags, distcmd, distflags, location, uploadflags, ff='', quiet=False):
        if not self.process.quiet:
            print 'running upload'

        echo = tee.After('running upload')
        if quiet:
            echo = tee.And(echo, tee.Not(tee.StartsWith('Submitting')))

        serverflags = ['--repository="%s"' % location]

        rc, lines = self._run_setup_py(
            ['egg_info'] + infoflags + [distcmd] + distflags +
            ['upload'] + serverflags + uploadflags,
            echo=echo,
            ff=ff)

        if rc == 0:
            if self._parse_upload_results(lines):
                return rc
        err_exit('upload failed')

    def _run_setup_py(self, args, echo=True, echo2=True, ff=''):
        """Run setup.py with monkey-patched setuptools.

        The patch forces setuptools to use the file-finder 'ff'.
        If 'ff' is the empty string, the patch is not applied.

        'args' contains the *list* of arguments that should be passed
        to setup.py.
        """
        python = self.python

        if ff:
            patched = WALK_REVCTRL % locals()
            setup_py = '-c"%(patched)s"' % locals()
        else:
            setup_py = 'setup.py %s' % ' '.join(args)

        rc, lines = self.process.popen(
            '"%(python)s" -B %(setup_py)s' % locals(), echo=echo, echo2=echo2)

        return rc, lines

    def _parse_egg_info_results(self, lines):
        for line in lines:
            if line.startswith("writing manifest file '"):
                return line.split("'")[1]
        return ''

    def _parse_dist_results(self, lines):
        # This relies on --formats=zip or --formats=egg
        for line in lines:
            if line.startswith("creating '") and "' and adding '" in line:
                return line.split("'")[1]
        return ''

    def _parse_register_results(self, lines):
        current, expect = None, 'running register'
        for line in lines:
            if line == expect:
                if line != 'Server response (200): OK':
                    current, expect = expect, 'Server response (200): OK'
                else:
                    if current == 'running register':
                        return True
        return False

    def _parse_upload_results(self, lines):
        current, expect = None, 'running upload'
        for line in lines:
            if line == expect:
                if line != 'Server response (200): OK':
                    current, expect = expect, 'Server response (200): OK'
                else:
                    if current == 'running upload':
                        return True
        return False


WALK_REVCTRL = """\
import os, sys
import distutils
import pkg_resources

from os.path import basename

class pythonpath_off(object):
    def __enter__(self):
        self.saved = os.environ.get('PYTHONPATH', '')
        if self.saved:
            del os.environ['PYTHONPATH']
    def __exit__(self, *ignored):
        if self.saved:
            os.environ['PYTHONPATH'] = self.saved

def walk_revctrl(dirname=''):
    file_finder = None
    items = []
    for ep in pkg_resources.iter_entry_points('setuptools.file_finders'):
        if %(ff)r == ep.name:
            distutils.log.info('using %%s file-finder', ep.name)
            file_finder = ep.load()
            finder_items = []
            with pythonpath_off():
                for item in file_finder(dirname):
                    if not basename(item).startswith(('.svn', '.hg', '.git')):
                        finder_items.append(item)
            distutils.log.info('%%d files found', len(finder_items))
            items.extend(finder_items)
    if file_finder is None:
        print >>sys.stderr, 'No %(ff)s file-finder; ' \
            'setuptools-%%s extension missing?' %% \
            'subversion' if %(ff)r.startswith('svn') else %(ff)r
        sys.exit(1)
    if not items:
        sys.exit(1)
    return items

import setuptools.command.egg_info
setuptools.command.egg_info.walk_revctrl = walk_revctrl

sys.argv = ['setup.py'] + %(args)r
import setup
"""

