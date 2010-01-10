import os
import tee

from os.path import abspath, join, isfile

from process import Process
from dirstack import chdir
from exit import err_exit


class Setuptools(object):
    """Interface to setuptools functions."""

    def __init__(self, defaults, process=None):
        self.process = process or Process()
        self.python = defaults.python

    def is_valid_package(self, dir):
        return isfile(join(dir, 'setup.py'))

    def check_valid_package(self, dir):
        if not self.is_valid_package(dir):
            err_exit('Not eggified (no setup.py found): %(dir)s' % locals())

    @chdir
    def get_package_info(self, dir):
        python = self.python
        rc, lines = self.process.popen(
            '"%(python)s" setup.py --name --version' % locals(), echo=False)
        if rc == 0 and len(lines) > 1:
            return lines[0], lines[1]
        err_exit('Bad setup.py')

    @chdir
    def run_dist(self, dir, distcmd, infoflags, distflags, scmtype='', quiet=False):
        echo = True
        if quiet:
            echo = tee.StartsWith('running')

        rc, lines = self._run_setup_py(
            ['egg_info'] + infoflags + [distcmd] + distflags,
            echo=echo,
            scmtype=scmtype)

        if rc == 0:
            filename = self._parse_dist_results(lines)
            if filename and isfile(filename):
                return abspath(filename)
        err_exit('Release failed')

    @chdir
    def run_upload(self, dir, location, distcmd, infoflags, distflags, uploadflags, scmtype=''):
        serverflags = ['--repository="%s"' % location]

        rc, lines = self._run_setup_py(
            ['egg_info'] + infoflags + [distcmd] + distflags +
            ['register'] + serverflags + ['upload'] + serverflags + uploadflags,
            echo=tee.NotBefore('running register'),
            scmtype=scmtype)

        if rc == 0:
            register_ok, upload_ok = self._parse_upload_results(lines)
            if register_ok and upload_ok:
                return rc
        err_exit('Upload failed')

    def _run_setup_py(self, args, echo=True, echo2=True, scmtype=''):
        """Run setup.py with monkey-patched setuptools.

        The patch forces setuptools to only use file-finders for the
        selected 'scmtype'.

        'args' contains the *list* of arguments that should be passed
        to setup.py.

        If 'scmtype' is the empty string, the patch is not applied.
        """
        python = self.python
        args = list(args)
        scmtype = scmtype.lower()
        patched = select_scm_patch % locals()

        if scmtype:
            setup_py = '-c"%(patched)s"' % locals()
        else:
            setup_py = 'setup.py %s' % ' '.join(args)

        rc, lines = self.process.popen(
            '"%(python)s" %(setup_py)s' % locals(), echo=echo, echo2=echo2)

        # Remove setup.pyc turd
        if isfile('setup.pyc'):
            os.remove('setup.pyc')

        return rc, lines

    def _parse_dist_results(self, lines):
        # This relies on --formats=zip (or egg)
        for line in lines:
            if line.startswith("creating '") and "' and adding" in line:
                return line.split("'")[1]
        return ''

    def _parse_upload_results(self, lines):
        register_ok = upload_ok = False
        current, expect = None, 'running register'
        for line in lines:
            if line == expect:
                if line != 'Server response (200): OK':
                    current, expect = expect, 'Server response (200): OK'
                else:
                    if current == 'running register':
                        register_ok = True
                        current, expect = expect, 'running upload'
                    elif current == 'running upload':
                        upload_ok = True
                        current, expect = expect, None
        return register_ok, upload_ok


select_scm_patch = """\
import os, sys
import distutils
import pkg_resources

def walk_revctrl(dirname=''):
    found = False
    for ep in pkg_resources.iter_entry_points('setuptools.file_finders'):
        if %(scmtype)r in ep.name:
            found = True
            distutils.log.info('using ' + ep.name + ' file-finder')
            for item in ep.load()(dirname):
                if not os.path.basename(item).startswith('.' + %(scmtype)r):
                    yield item
    if not found:
        print >>sys.stderr, 'No %(scmtype)s file-finder ' \
            '(setuptools_%(scmtype)s extension missing?)'
        sys.exit(1)

import setuptools.command.egg_info
setuptools.command.egg_info.walk_revctrl = walk_revctrl

sys.argv = ['setup.py'] + %(args)r
import setup
"""

