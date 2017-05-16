from __future__ import absolute_import
from __future__ import print_function

import os
import distutils.command
import pkg_resources

from os.path import abspath, join, isfile
from os.path import basename, dirname
from shutil import rmtree
from email import message_from_file

from .python import Python
from .process import Process
from .configparser import ConfigParser
from .chdir import chdir
from .exit import err_exit, warn
from .tee import *

OK_RESPONSE = 'Server response (200): OK'
GONE_RESPONSE = 'Server response (410):'


class Setuptools(object):
    """Interface to setuptools."""

    def __init__(self, process=None):
        self.process = process or Process(env=self.get_env())
        self.python = Python()

        self.infoflags = ['--tag-build=""', '--no-date']

        # setuptools < 33.1.0
        from setuptools.command.egg_info import egg_info
        if 'no-svn-revision' in getattr(egg_info, 'negative_opt', []):
            self.infoflags.append('--no-svn-revision')

    def get_env(self):
        # Make sure setuptools and its extensions are found if mkrelease
        # has been installed with zc.buildout
        path = []
        for name in ('setuptools', 'setuptools-hg', 'setuptools-git',
                     'setuptools-subversion', 'wheel'):
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
            print('running egg_info')

        echo = After('running egg_info')
        if quiet:
            echo = And(echo, StartsWith('running'))

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
            print('running', distcmd)

        echo = After('running %(distcmd)s' % locals())
        if quiet:
            echo = And(echo, StartsWith('running'))

        echo2 = On()
        if quiet and distcmd == 'bdist_wheel':
            echo2 = Not(And(StartsWith('Skipping'), EndsWith('(namespace package)')))

        checkcmd = []
        if 'check' in distutils.command.__all__:
            checkcmd = ['check']

        rc, lines = self._run_setup_py(
            ['egg_info'] + infoflags + checkcmd +
            [distcmd] + distflags,
            echo=echo,
            echo2=echo2,
            ff=ff)

        if rc == 0:
            filename = self._parse_dist_results(lines, distcmd)
            if filename and isfile(filename):
                return abspath(filename)
        err_exit('%(distcmd)s failed' % locals())

    @chdir
    def run_register(self, dir, infoflags, location, ff='', quiet=False):
        if not self.process.quiet:
            print('running register')

        echo = After('running register')
        if quiet:
            echo = And(echo, Not(Equals(OK_RESPONSE)))

        checkcmd = []
        if 'check' in distutils.command.__all__:
            checkcmd = ['check']

        serverflags = ['--repository="%(location)s"' % locals()]

        rc, lines = self._run_setup_py(
            ['egg_info'] + infoflags + checkcmd +
            ['register'] + serverflags,
            echo=echo,
            ff=ff)

        if rc == 0:
            if self._parse_register_results(lines):
                if not self.process.quiet and quiet:
                    print('OK')
                return rc
        err_exit('ERROR: register failed')

    @chdir
    def run_upload(self, dir, infoflags, distcmd, distflags, location, uploadflags, ff='', quiet=False):
        if not self.process.quiet:
            print('running upload')

        echo = After('running upload')
        if quiet:
            echo = And(echo, Not(Equals(OK_RESPONSE)))

        # distutils >= 3.4
        echo2 = Not(StartsWith('error: Upload failed'))

        serverflags = ['--repository="%(location)s"' % locals()]

        rc, lines = self._run_setup_py(
            ['egg_info'] + infoflags + [distcmd] + distflags +
            ['upload'] + serverflags + uploadflags,
            echo=echo,
            echo2=echo2,
            ff=ff)

        if rc == 0:
            if self._parse_upload_results(lines):
                if not self.process.quiet and quiet:
                    print('OK')
                return rc
        err_exit('ERROR: upload failed')

    def _run_setup_py(self, args, echo=True, echo2=True, ff=''):
        """Run setup.py with monkey-patched setuptools.

        The patch forces setuptools to use the file-finder 'ff'.
        If 'ff' is the empty string, the patch is not applied.

        'args' is the list of arguments that should be passed to
        setup.py.
        """
        python = self.python

        if ff:
            patch = WALK_REVCTRL % locals()
            setup_py = '-c"%(patch)s"' % locals()
        else:
            setup_py = 'setup.py %s' % ' '.join(args)

        rc, lines = self.process.popen(
            '"%(python)s" %(setup_py)s' % locals(), echo=echo, echo2=echo2)

        if isfile('setup.pyc'):
            os.remove('setup.pyc')

        return rc, lines

    def _parse_egg_info_results(self, lines):
        for line in lines:
            if line.startswith("writing manifest file '"):
                return line.split("'")[1]
        return ''

    def _parse_dist_results(self, lines, distcmd):
        if distcmd == 'bdist_wheel':
            return self._parse_wheel_results(lines)
        else:
            return self._parse_sdist_bdist_results(lines)

    def _parse_sdist_bdist_results(self, lines):
        # This relies on --formats=zip or --formats=egg
        for line in lines:
            if line.startswith("creating '") and "' and adding '" in line:
                return line.split("'")[1]
        # Must be --formats=gztar then
        for line in lines:
            if line.startswith('Writing ') and line.endswith('setup.cfg'):
                pkgname = basename(dirname(line[8:])) + '.tar.gz'
                return join('dist', pkgname)
        return ''

    def _parse_wheel_results(self, lines):
        # This relies on --keep-temp
        wheelfile = ''
        for line in lines:
            if line.startswith('creating ') and line.endswith('WHEEL'):
                wheelfile = line[9:]
        result = ''
        if wheelfile:
            tags = []
            pure = False
            universal = False
            with open(wheelfile, 'rt') as fp:
                msg = message_from_file(fp)
                tags = msg.get_all('Tag')
                pure = msg.get('Root-Is-Purelib', '') == 'true'
                universal = len(tags) > 1
            if tags:
                tag = tags[0]
                if pure and universal:
                    if tag.startswith(('py2-', 'py3-')):
                        tag = 'py2.py3-' + tag[4:]
                pkgname = basename(dirname(wheelfile))[:-10]
                pkgname = '-'.join((pkgname, tag)) + '.whl'
                result = join('dist', pkgname)
            # Clean up or the next build might contain crap
            rmtree(dirname(dirname(wheelfile)))
        return result

    def _parse_register_results(self, lines):
        return self._parse_server_response_2017(
            lines, 'running register', (OK_RESPONSE, GONE_RESPONSE))

    def _parse_upload_results(self, lines):
        return self._parse_server_response_2017(
            lines, 'running upload', (OK_RESPONSE,))

    def _parse_server_response_2017(self, lines, match, then_match):
        current, expect = '', (match,)
        for line in lines:
            if [x for x in expect if line.startswith(x)]:
                if not current:
                    current, expect = match, then_match
                elif current == match:
                    return True
        return False

    def _parse_server_response(self, lines, match):
        current, expect = '', match
        for line in lines:
            if line == expect:
                if expect == match:
                    current, expect = match, OK_RESPONSE
                elif current == match:
                    return True
        return False


WALK_REVCTRL = """\
from __future__ import print_function
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
        print('No %(ff)s file-finder; setuptools-%%s extension missing?' %%
            ('subversion' if %(ff)r.startswith('svn') else %(ff)r),
            file=sys.stderr)
        sys.exit(1)
    if not items:
        sys.exit(1)
    return items

import setuptools.command.egg_info
setuptools.command.egg_info.walk_revctrl = walk_revctrl

sys.argv = ['setup.py'] + %(args)r
import setup
"""

