# 'from jarn.mkrelease import setup; setup.run(%(args)r, ff=%(ff)r)'

from __future__ import absolute_import

import sys
import os
import glob
import setuptools # XXX
import distutils
import pkg_resources

from os.path import basename, isdir, join, exists
from functools import partial


class pythonpath_off(object):
    """Temporarily delete the PYTHONPATH environment variable.
    """

    def __enter__(self):
        self.saved = os.environ.get('PYTHONPATH', '')
        if self.saved:
            del os.environ['PYTHONPATH']

    def __exit__(self, *ignored):
        if self.saved:
            os.environ['PYTHONPATH'] = self.saved


def walk_revctrl(dirname='', ff=''):
    """Return files found by the file-finder 'ff'.
    """
    file_finder = None
    items = []

    #if not ff:
    #    distutils.log.error('No file-finder passed to walk_revctrl')
    #    sys.exit(1)

    for ep in pkg_resources.iter_entry_points('setuptools.file_finders'):
        if ff == ep.name:
            distutils.log.info('using %s file-finder', ep.name)
            file_finder = ep.load()
            finder_items = []
            with pythonpath_off():
                for item in file_finder(dirname):
                    if not basename(item).startswith(('.svn', '.hg', '.git')):
                        finder_items.append(item)
            distutils.log.info('%d files found', len(finder_items))
            items.extend(finder_items)

    #if file_finder is None:
    #    distutils.log.error('Failed to load %s file-finder; setuptools-%s extension missing?',
    #        ff, 'subversion' if ff == 'svn' else ff)
    #    sys.exit(1)

    # Returning a non-empty list prevents egg_info from reading the
    # existing SOURCES.txt
    return items or ['']


def no_walk_revctrl(dirname=''):
    """Return empty list.
    """
    # Returning a non-empty list prevents egg_info from reading the
    # existing SOURCES.txt
    return ['']


def cleanup_pycache():
    """Remove .pyc files we leave around because of import.
    """
    try:
        for file in glob.glob('setup.py[co]'):
            os.remove(file)
        if isdir('__pycache__'):
            for file in glob.glob(join('__pycache__', 'setup.*.py[co]')):
                os.remove(file)
            if not glob.glob(join('__pycache__', '*')):
                os.rmdir('__pycache__')
    except (IOError, OSError):
        pass


def run(args, ff=''):
    """Run setup.py with monkey patches applied.
    """
    # Set log level INFO in setuptools >= 60.0.0 with local distutils
    import setuptools
    import distutils
    if hasattr(distutils.log, 'set_verbosity'):
        distutils.log.set_verbosity(1)

    # Required in setuptools >= 60.6.0, <= 60.9.1
    import distutils.dist
    if hasattr(distutils.dist.log, 'set_verbosity'):
        distutils.dist.log.set_verbosity(1)

    import setuptools.command.egg_info
    if not ff or ff == 'none':
        setuptools.command.egg_info.walk_revctrl = no_walk_revctrl
    else:
        setuptools.command.egg_info.walk_revctrl = partial(walk_revctrl, ff=ff)

    sys.argv = ['setup.py'] + args
    try:
        if exists('setup.py'):
            import setup
        else:
            setuptools.setup()
    finally:
        cleanup_pycache()

