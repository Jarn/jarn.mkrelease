from __future__ import absolute_import
from __future__ import print_function

import locale
try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    pass

import pkg_resources
__version__ = pkg_resources.get_distribution('jarn.mkrelease').version

import sys
import os
import getopt
import tempfile
import shutil

from os.path import abspath, join, expanduser, exists, isfile
from itertools import chain

from .python import Python
from .setuptools import Setuptools
from .twine import Twine
from .scp import SCP
from .scm import SCMFactory
from .urlparser import URLParser
from .configparser import ConfigParser
from .exit import err_exit, msg_exit, warn
from .colors import green, blue

MAXALIASDEPTH = 23

VERSION = "jarn.mkrelease %s" % __version__
USAGE = "Try 'mkrelease --help' for more information"

HELP = """\
Usage: mkrelease [options] [scm-sandbox|scm-url [rev]]

Python package releaser

Options:
  -C, --no-commit       Do not commit modified files from the sandbox.
  -T, --no-tag          Do not tag the release in SCM.
  -P, --no-push         Do not push commits and tags upstream.
  -R, --no-register     Do not register the release with dist-location.
  -S, --no-upload       Do not upload the release to dist-location.
  -n, --dry-run         Dry-run; equivalent to -CTPRS.

  --svn, --hg, --git    Select the SCM type. Only required if the SCM type
                        cannot be guessed from the argument.

  -d dist-location, --dist-location=dist-location
                        An scp destination specification, an index server
                        configured in ~/.pypirc, or an alias name for
                        either. This option may be specified more than once.

  -s, --sign            Sign the release with GnuPG.
  -i identity, --identity=identity
                        The GnuPG identity to sign with. Implies -s.

  -z, --zip             Release a zip archive.
  -g, --gztar           Release a tar.gz archive (default).
  -b, --egg             Release a binary egg.
  -w, --wheel           Release a wheel file (default).

  -m, --manifest-only   Ignore setuptools extensions and collect files via
                        MANIFEST.in only.
  -e, --develop         Allow setuptools build tags. Implies -T.
  -q, --quiet           Suppress output of setuptools commands.

  -t twine, --twine=twine
                        Override the twine executable used.

  -c config-file, --config-file=config-file
                        Use config-file instead of the default ~/.mkrelease.

  -l, --list-locations  List known dist-locations and exit.
  -h, --help            Print this help message and exit.
  -v, --version         Print the version string and exit.

  --no-color            Disable output colors.
  --non-interactive     Do not prompt for username and password if the
                        required credentials are missing.

Arguments:
  scm-sandbox           A local SCM sandbox. Defaults to the current working
                        directory.
  scm-url [rev]         The URL of a remote SCM repository. The optional rev
                        argument specifies a branch or tag to check out.
"""


class Defaults(object):

    def __init__(self, config_file):
        """Read config files.
        """
        parser = ConfigParser(warn)
        parser.read((expanduser('~/.pypirc'), config_file))

        self.warnings = parser.warnings

        main_section = 'mkrelease'
        if not parser.has_section(main_section) and parser.has_section('defaults'):
            main_section = 'defaults' # BBB

        self.distbase = parser.getstring(main_section, 'distbase', '')
        self.distdefault = parser.getlist(main_section, 'distdefault', [])
        self.distdefault = parser.getlist(main_section, 'dist-location', self.distdefault)

        self.commit = parser.getboolean(main_section, 'commit', True)
        self.tag = parser.getboolean(main_section, 'tag', True)
        self.register = parser.getboolean(main_section, 'register', False)
        self.upload = parser.getboolean(main_section, 'upload', True)
        self.formats = parser.getlist(main_section, 'formats', [])
        self.sign = parser.getboolean(main_section, 'sign', False)
        self.identity = parser.getstring(main_section, 'identity', '')
        self.push = parser.getboolean(main_section, 'push', True)
        self.manifest = parser.getboolean(main_section, 'manifest-only', False)
        self.develop = parser.getboolean(main_section, 'develop', False)
        self.quiet = parser.getboolean(main_section, 'quiet', False)
        self.twine = parser.getstring(main_section, 'twine', '')
        self.interactive = parser.getboolean(main_section, 'interactive', True)

        for format in self.formats:
            if format not in ('zip', 'gztar', 'egg', 'wheel'):
                warn("Ignoring unknown format '%(format)s'" % locals())

        self.aliases = {}
        for key, value in parser.items('aliases', []):
            self.aliases[key] = parser.to_list(value)

        class ServerInfo(object):
            def __init__(self, server_section):
                self.sign = parser.getboolean(server_section, 'sign', None)
                self.identity = parser.getstring(server_section, 'identity', None)
                self.register = parser.getboolean(server_section, 'register', None)

        self.servers = {}
        for server in parser.getlist('distutils', 'index-servers', []):
            self.servers[server] = ServerInfo(server)

        # pypi always works
        if 'pypi' not in self.servers:
            self.servers['pypi'] = ServerInfo('pypi')

        if os.environ.get('JARN_RUN') == '1':
            if parser.warnings:
                err_exit('mkrelease: Bad configuration')

    def get_known_locations(self):
        """Return a set of known locations.
        """
        return set(chain(self.aliases, self.servers))


class Locations(object):

    def __init__(self, defaults):
        self.distbase = defaults.distbase
        self.distdefault = defaults.distdefault
        self.aliases = defaults.aliases
        self.servers = defaults.servers
        self.locations = []
        self.urlparser = URLParser()

    def __len__(self):
        """Return number of locations.
        """
        return len(self.locations)

    def __iter__(self):
        """Iterate over locations.
        """
        return iter(self.locations)

    def extend(self, location):
        """Extend list of locations.
        """
        self.locations.extend(location)

    def is_server(self, location):
        """Return True if 'location' is an index server.
        """
        return location in self.servers

    def is_ssh_url(self, location):
        """Return True if 'location' is an scp:// or sftp:// URL.
        """
        return self.urlparser.get_scheme(location) in ('scp', 'sftp')

    def is_valid_ssh_url(self, location):
        """Return True if 'location' is a valid scp:// or sftp:// URL.
        """
        scheme = self.urlparser.get_scheme(location)
        return scheme in ('scp', 'sftp') and len(location) > len(scheme)+3

    def has_host(self, location):
        """Return True if 'location' contains a host part.
        """
        return self.urlparser.is_ssh_url(location)

    def join(self, distbase, location):
        """Join 'distbase' and 'location' in such way that the
        result is a valid scp destination.
        """
        sep = ''
        if distbase and distbase[-1] not in (':', '/'):
            sep = '/'
        return distbase + sep + location

    def get_location(self, location, depth=0):
        """Resolve aliases and apply distbase.
        """
        if not location:
            return []
        if location in self.aliases:
            res = []
            if depth > MAXALIASDEPTH:
                err_exit('mkrelease: Maximum alias depth exceeded: %(location)s' % locals())
            for loc in self.aliases[location]:
                res.extend(self.get_location(loc, depth+1))
            return res
        if self.is_server(location):
            return [location]
        if location == 'pypi':
            return [location]
        if self.urlparser.is_url(location):
            return [location]
        if not self.has_host(location) and self.distbase:
            return [self.join(self.distbase, location)]
        return [location]

    def get_default_location(self):
        """Return the default location.
        """
        res = []
        for location in self.distdefault:
            res.extend(self.get_location(location))
        return res

    def check_empty_locations(self, locations=None):
        """Fail if 'locations' is empty.
        """
        if locations is None:
            locations = self.locations
        if not locations:
            err_exit('mkrelease: Option -d is required\n%s' % USAGE)

    def check_valid_locations(self, locations=None):
        """Fail if 'locations' contains bad destinations.
        """
        if locations is None:
            locations = self.locations
        for location in locations:
            if (not self.is_server(location) and
                not self.is_valid_ssh_url(location) and
                not self.has_host(location)):
                err_exit("mkrelease: Unknown location: %(location)s\n"
                         "Try 'mkrelease --list-locations' to list known servers "
                         "and aliases" % locals())


class ReleaseMaker(object):

    def __init__(self, args):
        """Initialize.
        """
        self.args = args

    def set_defaults(self, config_file):
        """Set defaults.
        """
        self.defaults = Defaults(config_file)
        self.locations = Locations(defaults=self.defaults)
        self.python = Python()
        self.setuptools = Setuptools()
        self.twine = Twine(defaults=self.defaults)
        self.scp = SCP(defaults=self.defaults)
        self.scms = SCMFactory()
        self.urlparser = URLParser()
        self.skipcommit = not self.defaults.commit
        self.skiptag = not self.defaults.tag
        self.skipregister = False   # per server
        self.skipupload = False     # special
        self.push = self.defaults.push
        self.develop = False        # special
        self.quiet = self.defaults.quiet
        self.sign = False           # per server
        self.list = False
        self.manifest = self.defaults.manifest
        self.identity = ''          # per server
        self.branch = ''
        self.scmtype = ''
        self.infoflags = []
        self.formats = []
        self.distributions = []
        self.directory = os.curdir
        self.scm = None

    def reset_defaults(self, config_file):
        """Reset defaults.
        """
        if not exists(config_file):
            err_exit('mkrelease: No such file: %(config_file)s' % locals())
        if not isfile(config_file):
            err_exit('mkrelease: Not a file: %(config_file)s' % locals())
        if not os.access(config_file, os.R_OK):
            err_exit('mkrelease: Cannot read %(config_file)s' % locals())
        self.set_defaults(config_file)

    def parse_options(self, args, depth=0):
        """Parse command line options.
        """
        try:
            options, remaining_args = getopt.gnu_getopt(args,
                'CPRSTbc:d:eghi:lmnpqst:vwz',
                ('no-commit', 'no-tag', 'no-register', 'no-upload', 'dry-run',
                 'sign', 'identity=', 'dist-location=', 'version', 'help',
                 'push', 'quiet', 'svn', 'hg', 'git', 'develop', 'binary',
                 'list-locations', 'config-file=', 'wheel', 'zip', 'gztar',
                 'manifest-only', 'trace', 'egg', 'no-push', 'twine=',
                 'no-color', 'non-interactive'))
        except getopt.GetoptError as e:
            err_exit('mkrelease: %s\n%s' % (e.msg.capitalize(), USAGE))

        for name, value in options:
            if name in ('-C', '--no-commit'):
                self.skipcommit = True
            elif name in ('-T', '--no-tag'):
                self.skiptag = True
            elif name in ('-R', '--no-register'):
                self.skipregister = True
            elif name in ('-S', '--no-upload'):
                self.skipupload = True
            elif name in ('-n', '--dry-run'):
                self.skipcommit = self.skiptag = self.skipregister = self.skipupload = True
            elif name in ('-p', '--push'):      # undocumented
                self.push = True
            elif name in ('-P', '--no-push'):
                self.push = False
            elif name in ('-q', '--quiet'):
                self.quiet = True
            elif name in ('-s', '--sign'):
                self.sign = True
            elif name in ('-i', '--identity'):
                self.identity = value
            elif name in ('-d', '--dist-location'):
                self.locations.extend(self.locations.get_location(value))
            elif name in ('-l', '--list-locations'):
                self.list = True
            elif name in ('-m', '--manifest-only'):
                self.manifest = True
            elif name in ('-h', '--help'):
                msg_exit(HELP)
            elif name in ('-v', '--version'):
                msg_exit(VERSION)
            elif name in ('--svn', '--hg', '--git'):
                self.scmtype = name[2:]
            elif name in ('-e', '--develop'):
                self.develop = True
            elif name in ('-z', '--zip'):
                self.formats.append('zip')
            elif name in ('-g', '--gztar'):
                self.formats.append('gztar')
            elif name in ('-b', '--binary', '--egg'):
                self.formats.append('egg')
            elif name in ('-w', '--wheel'):
                self.formats.append('wheel')
            elif name in ('--trace',):          # undocumented
                os.environ['JARN_TRACE'] = '1'
            elif name in ('--no-color',):
                os.environ['JARN_NO_COLOR'] = '1'
            elif name in ('-t', '--twine'):
                self.twine.twine = expanduser(value)
            elif name in ('--non-interactive',):
                self.twine.interactive = False
                self.scp.interactive = False
            elif name in ('-c', '--config-file') and depth == 0:
                self.reset_defaults(expanduser(value))
                return self.parse_options(args, depth+1)

        return remaining_args

    def list_locations(self):
        """Print known dist-locations and exit.
        """
        known = self.defaults.get_known_locations()
        for default in self.defaults.distdefault:
            if default not in known:
                known.add(default)
        for location in sorted(known):
            if location in self.defaults.distdefault:
                print(location, '(default)')
            else:
                print(location)
        sys.exit(0)

    def get_skipregister(self, location=None):
        """Return true if the register command is disabled (for the given server.)
        """
        if location is None:
            return self.skipregister or not self.defaults.register
        else:
            server = self.defaults.servers[location]
            if self.skipregister:
                return True
            elif server.register is not None:
                if not self.defaults.register and self.get_skipupload():
                    return True # prevent override
                return not server.register
            elif not self.defaults.register:
                return True
            return False

    def get_skipupload(self):
        """Return true if the upload command is disabled.
        """
        return self.skipupload or not self.defaults.upload

    def get_uploadflags(self, location):
        """Return uploadflags for the given server.
        """
        uploadflags = []
        server = self.defaults.servers[location]

        if self.sign:
            uploadflags.append('--sign')
        elif server.sign is not None:
            if server.sign:
                uploadflags.append('--sign')
        elif self.defaults.sign:
            uploadflags.append('--sign')

        if self.identity:
            if '--sign' not in uploadflags:
                uploadflags.append('--sign')
            uploadflags.append('--identity="%s"' % self.identity)
        elif '--sign' in uploadflags:
            if server.identity is not None:
                if server.identity:
                    uploadflags.append('--identity="%s"' % server.identity)
            elif self.defaults.identity:
                uploadflags.append('--identity="%s"' % self.defaults.identity)

        return uploadflags

    def get_python(self):
        """Get the Python interpreter.
        """
        self.python.check_valid_python()

    def get_options(self):
        """Process the command line.
        """
        args = self.parse_options(self.args)

        if args:
            self.directory = args[0]

        if self.develop:
            self.skiptag = True
        if not self.develop:
            self.develop = self.defaults.develop
        if not self.develop:
            self.infoflags = self.setuptools.infoflags

        if not self.formats:
            self.formats = self.defaults.formats

        for format in self.formats:
            if format == 'zip':
                self.distributions.append(('sdist', ['--formats="zip"']))
            elif format == 'gztar':
                self.distributions.append(('sdist', ['--formats="gztar"']))
            elif format == 'egg':
                self.distributions.append(('bdist', ['--formats="egg"']))
            elif format == 'wheel':
                self.distributions.append(('bdist_wheel', []))

        if not self.distributions:
            self.distributions.append(('sdist', ['--formats="gztar"']))
            self.distributions.append(('bdist_wheel', []))

        if self.list:
            self.list_locations()

        if not self.locations:
            self.locations.extend(self.locations.get_default_location())

        if len(args) > 1:
            if self.urlparser.is_url(self.directory):
                self.branch = args[1]
            elif self.urlparser.is_ssh_url(self.directory):
                self.branch = args[1]
            else:
                err_exit('mkrelease: Invalid arguments\n%s' % USAGE)

        if len(args) > 2:
            err_exit('mkrelease: Too many arguments\n%s' % USAGE)

        if not (self.skipregister and self.skipupload):
            if not (self.get_skipregister() and self.get_skipupload()):
                self.locations.check_empty_locations()
            self.locations.check_valid_locations()

    def get_package(self):
        """Get the URL or sandbox to release.
        """
        directory = self.directory
        develop = self.develop
        scmtype = self.scmtype

        self.scm = self.scms.get_scm(scmtype, directory)

        if self.scm.is_valid_url(directory):
            directory = self.urlparser.abspath(directory)

            self.remoteurl = directory
            self.isremote = self.push = True
        else:
            directory = abspath(expanduser(directory))
            self.isremote = False

            self.scm.check_valid_sandbox(directory)
            self.setuptools.check_valid_package(directory)

            name, version = self.setuptools.get_package_info(directory, develop)
            print(blue('Releasing %(name)s %(version)s' % locals()))

            if not self.skipcommit:
                if self.scm.is_dirty_sandbox(directory):
                    self.scm.commit_sandbox(directory, name, version, self.push)

    def make_release(self):
        """Build and distribute the package.
        """
        directory = self.directory
        infoflags = self.infoflags
        branch = self.branch
        develop = self.develop
        scmtype = self.scm.name

        tempdir = abspath(tempfile.mkdtemp(prefix='mkrelease-'))
        try:
            if self.isremote:
                directory = join(tempdir, 'build')
                self.scm.clone_url(self.remoteurl, directory)
            else:
                directory = abspath(expanduser(directory))

            self.scm.check_valid_sandbox(directory)

            if self.isremote:
                branch = self.scm.make_branchid(directory, branch)
                if branch:
                    self.scm.switch_branch(directory, branch)
                if scmtype != 'svn':
                    branch = self.scm.get_branch_from_sandbox(directory)
                    print('Releasing revision', branch)

            self.setuptools.check_valid_package(directory)

            if not (self.skipcommit and self.skiptag):
                self.scm.check_dirty_sandbox(directory)
                self.scm.check_unclean_sandbox(directory)

            name, version = self.setuptools.get_package_info(directory, develop)
            if self.isremote:
                print(blue('Releasing %(name)s %(version)s' % locals()))

            if not self.skiptag:
                print('Tagging', name, version)
                tagid = self.scm.make_tagid(directory, version)
                self.scm.check_tag_exists(directory, tagid)
                self.scm.create_tag(directory, tagid, name, version, self.push)

            if self.manifest:
                scmtype = 'none'

            distfiles = []
            for distcmd, distflags in self.distributions:
                manifest = self.setuptools.run_egg_info(
                    directory, infoflags, scmtype, self.quiet)
                distfile = self.setuptools.run_dist(
                    directory, infoflags, distcmd, distflags, scmtype, self.quiet)
                distfiles.append(distfile)

            firstserver = True
            for location in self.locations:
                if self.locations.is_server(location):
                    if not self.get_skipregister(location):
                        self.twine.run_register(
                            directory, distfiles, location, self.quiet)
                    if not self.get_skipupload():
                        uploadflags = self.get_uploadflags(location)
                        if '--sign' in uploadflags:
                            if firstserver:
                                for distfile in distfiles:
                                    try:
                                        os.remove(distfile+'.asc')
                                    except (IOError, OSError):
                                        pass
                                firstserver = False
                        self.twine.run_upload(
                            directory, distfiles, location, uploadflags, self.quiet)
                else:
                    if not self.skipupload:
                        if self.locations.is_ssh_url(location):
                            scheme, location = self.urlparser.to_ssh_url(location)
                            self.scp.run_upload(scheme, distfiles, location)
                        else:
                            self.scp.run_upload('scp', distfiles, location)
        finally:
            shutil.rmtree(tempdir)

    def get_env(self):
        os.environ['JARN_RUN'] = '1'

        for arg in self.args:
            if arg in ('--no-col', '--no-colo', '--no-color'):
                os.environ['JARN_NO_COLOR'] = '1'
                break

    def run(self):
        self.get_env()
        self.set_defaults(expanduser('~/.mkrelease'))
        self.get_python()
        self.get_options()
        self.get_package()
        self.make_release()
        print(green('done'))


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    try:
        ReleaseMaker(args).run()
    except SystemExit as e:
        return e.code
    return 0


if __name__ == '__main__':
    sys.exit(main())

