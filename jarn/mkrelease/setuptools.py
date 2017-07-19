from __future__ import absolute_import
from __future__ import print_function

import os
import distutils.command
import pkg_resources

from os.path import abspath, join, isfile
from os.path import basename, dirname

from .python import Python
from .process import Process
from .configparser import ConfigParser
from .chdir import chdir
from .exit import err_exit, warn
from .tee import *

OK_RESPONSE = 'Server response (200): OK'
GONE_RESPONSE = 'Server response (410):'

RUN_SETUP = 'from jarn.mkrelease import setup; setup.run(%(args)r, ff=%(ff)r)'


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
                     'setuptools-subversion', 'wheel', 'keyring'):
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
            if distflags == ['--formats="gztar"']:
                filename = self._parse_gztar_results(lines)
            else:
                filename = self._parse_dist_results(lines)
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

        if distcmd == 'bdist_wheel':
            echo2 = And(echo2, Not(And(StartsWith('Skipping'), EndsWith('(namespace package)'))))

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
            setup_py = '-c"%s"' % (RUN_SETUP % locals())
        else:
            setup_py = 'setup.py %s' % ' '.join(args)

        rc, lines = self.process.popen(
            '"%(python)s" %(setup_py)s' % locals(), echo=echo, echo2=echo2)

        return rc, lines

    def _parse_egg_info_results(self, lines):
        for line in lines:
            if line.startswith("writing manifest file '"):
                return line.split("'")[1]
        return ''

    def _parse_dist_results(self, lines):
        # This relies on --formats=zip or --formats=egg or bdist_wheel+patch
        for line in lines:
            if line.startswith("creating '") and "' and adding '" in line:
                return line.split("'")[1]
        return ''

    def _parse_gztar_results(self, lines):
        # This relies on --formats=gztar and a default --dist-dir
        for line in lines:
            if line.startswith('Writing ') and line.endswith('setup.cfg'):
                pkgname = basename(dirname(line[8:])) + '.tar.gz'
                return join('dist', pkgname)
        return ''

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

