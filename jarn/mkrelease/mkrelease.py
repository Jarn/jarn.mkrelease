import sys
import os
import getopt
import tempfile
import shutil
import ConfigParser

from os.path import abspath, join, expanduser, isfile

from python import Python
from setuptools import Setuptools
from scp import SCP
from scm import SCMFactory
from exit import msg_exit, err_exit

pypiurl = "http://pypi.python.org/pypi"
maxaliasdepth = 23

version = "jarn.mkrelease 3.0.3"
usage = "Try 'mkrelease --help' for more information."
help = """\
Usage: mkrelease [options] [scm-url|scm-sandbox]

Python egg releaser

Options:
  -C, --no-commit     Do not commit modified files from the sandbox.
  -T, --no-tag        Do not tag the release in SCM.
  -S, --no-upload     Do not upload the release to dist-location.
  -n, --dry-run       Dry-run; equivalent to -CTS.

  --svn, --hg, --git  Select the SCM type. Only required if the SCM type
                      cannot be guessed from the argument.

  -d dist-location, --dist-location=dist-location
                      An scp destination specification, or an index server
                      configured in ~/.pypirc, or an alias name for either.
                      This option may be specified more than once.

  -s, --sign          Sign the release with GnuPG.
  -i identity, --identity=identity
                      The GnuPG identity to sign with.

  -p, --push          Push changes upstream (Mercurial and Git).
  -e, --develop       Allow version number extensions.
  -b, --binary        Release a binary egg.
  -q, --quiet         Suppress output of setuptools commands.
  -h, --help          Print this help message and exit.
  -v, --version       Print the version string and exit.

  scm-url             The URL of a remote SCM repository.
  scm-sandbox         A local SCM sandbox; defaults to the current working
                      directory.
"""


class Defaults(object):

    def __init__(self):
        """Read config files.
        """
        self.parser = ConfigParser.ConfigParser()
        self.parser.read((expanduser('~/.pypirc'),
                          expanduser('~/.mkrelease')))

        def get(section, key, default=None):
            if self.parser.has_option(section, key):
                return self.parser.get(section, key)
            return default

        def getboolean(section, key, default=None):
            if self.parser.has_option(section, key):
                return self.parser.getboolean(section, key)
            return default

        self.distbase = get('defaults', 'distbase', '')
        self.distdefault = get('defaults', 'distdefault', '')

        self.sign = getboolean('defaults', 'sign', False)
        self.identity = get('defaults', 'identity', '')

        self.aliases = {}
        if self.parser.has_section('aliases'):
            for key, value in self.parser.items('aliases'):
                self.aliases[key] = value.split()

        self.servers = {}
        for server in get('distutils', 'index-servers', '').split():
            url = get(server, 'repository', pypiurl)
            self.servers[server] = True
            self.servers[url] = True

        self.python = sys.executable


class Locations(object):

    def __init__(self, defaults):
        self.distbase = defaults.distbase
        self.distdefault = defaults.distdefault
        self.aliases = defaults.aliases
        self.servers = defaults.servers
        self.locations = []

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

    def has_host(self, location):
        """Return True if 'location' contains a host part.
        """
        colon = location.find(':')
        slash = location.find('/')
        return colon > 0 and (slash < 0 or slash > colon)

    def get_location(self, location, depth=0):
        """Resolve aliases and apply distbase.
        """
        if not location:
            return []
        if location in self.aliases:
            res = []
            if depth > maxaliasdepth:
                err_exit('Maximum alias depth exceeded: %(location)s' % locals())
            for loc in self.aliases[location]:
                res.extend(self.get_location(loc, depth+1))
            return res
        if self.is_server(location):
            return [location]
        if location == 'pypi':
            err_exit('No configuration found for server: pypi')
        if not self.has_host(location) and self.distbase:
            sep = '/'
            if self.distbase[-1] in (':', '/'):
                sep = ''
            return [self.distbase + sep + location]
        return [location]

    def get_default_location(self):
        """Return the default location.
        """
        return self.get_location(self.distdefault)

    def check_valid_locations(self, locations=None):
        """Fail if 'locations' is empty or contains bad scp destinations.
        """
        if locations is None:
            locations = self.locations
        if not locations:
            err_exit('mkrelease: option -d is required\n%s' % usage)
        for location in locations:
            if not self.is_server(location) and not self.has_host(location):
                err_exit('Scp destination must contain host part: %(location)s' % locals())


class ReleaseMaker(object):

    def __init__(self, args):
        """Set defaults.
        """
        self.skipcheckin = False
        self.skiptag = False
        self.skipupload = False
        self.push = False
        self.quiet = False
        self.distcmd = 'sdist'
        self.infoflags = ['--no-svn-revision', '--no-date', '--tag-build=""']
        self.distflags = ['--formats="zip"']
        self.uploadflags = []
        self.directory = os.curdir
        self.defaults = Defaults()
        self.locations = Locations(self.defaults)
        self.python = Python(self.defaults)
        self.setuptools = Setuptools(self.defaults)
        self.scp = SCP()
        self.scms = SCMFactory()
        self.scm = None
        self.scmtype = ''
        self.args = args

    def parse_options(self, args):
        """Parse command line options.
        """
        try:
            options, args = getopt.gnu_getopt(args, 'CSTbd:ehi:npqsv',
                ('no-commit', 'no-tag', 'no-upload', 'dry-run',
                 'sign', 'identity=', 'dist-location=', 'version', 'help',
                 'push', 'quiet', 'svn', 'hg', 'git', 'develop', 'binary'))
        except getopt.GetoptError, e:
            err_exit('mkrelease: %s\n%s' % (e.msg, usage))

        for name, value in options:
            if name in ('-C', '--no-commit'):
                self.skipcheckin = True
            elif name in ('-T', '--no-tag'):
                self.skiptag = True
            elif name in ('-S', '--no-upload'):
                self.skipupload = True
            elif name in ('-n', '--dry-run'):
                self.skipcheckin = self.skiptag = self.skipupload = True
            elif name in ('-p', '--push'):
                self.push = True
            elif name in ('-q', '--quiet'):
                self.quiet = True
            elif name in ('-s', '--sign'):
                self.uploadflags.append('--sign')
            elif name in ('-i', '--identity'):
                self.uploadflags.append('--identity="%s"' % value)
            elif name in ('-d', '--dist-location'):
                self.locations.extend(self.locations.get_location(value))
            elif name in ('-v', '--version'):
                msg_exit(version)
            elif name in ('-h', '--help'):
                msg_exit(help)
            elif name in ('--svn', '--hg', '--git'):
                self.scmtype = name[2:]
            elif name in ('-e', '--develop'):
                self.skiptag = True
                self.infoflags = []
            elif name in ('-b', '--binary'):
                self.distcmd = 'bdist'
                self.distflags = ['--formats="egg"']

        return args

    def finish_options(self, args):
        """Post-process command line options.
        """
        if not self.uploadflags and self.defaults.sign:
            self.uploadflags.append('--sign')

        if self.uploadflags and '--sign' not in self.uploadflags:
            self.uploadflags.append('--sign')

        if len(set(self.uploadflags)) == 1 and self.defaults.identity:
            self.uploadflags.append('--identity="%s"' % self.defaults.identity)

        if not self.locations:
            self.locations.extend(self.locations.get_default_location())

        if not self.skipupload:
            self.locations.check_valid_locations()

        if args:
            err_exit('mkrelease: too many arguments\n%s' % usage)

    def get_python(self):
        """Get the Python interpreter.
        """
        if not self.python.is_valid_distutils():
            self.python.check_valid_python()

    def get_options(self):
        """Parse the command line.
        """
        args = self.parse_options(self.args)

        if args:
            self.directory = args.pop(0)

        self.finish_options(args)

    def get_package(self):
        """Get the URL or sandbox to release.
        """
        directory = self.directory
        scmtype = self.scmtype

        self.scm = self.scms.guess_scm(scmtype, directory)

        if self.scm.is_valid_url(directory):
            self.remoteurl = directory
            self.isremote = self.push = True

            if directory.startswith('file://') and not directory.startswith('file:///'):
                err_exit('File URLs must be absolute: %(directory)s' % locals())
        else:
            directory = abspath(expanduser(directory))
            self.isremote = False

            self.scm.check_valid_sandbox(directory)
            self.setuptools.check_valid_package(directory)

            name, version = self.setuptools.get_package_info(directory)
            print 'Releasing', name, version

            if not self.skipcheckin:
                if self.scm.is_dirty_sandbox(directory):
                    self.scm.checkin_sandbox(directory, name, version, self.push)

    def make_release(self):
        """Build and distribute the egg.
        """
        tempdir = abspath(tempfile.mkdtemp(prefix='mkrelease-'))
        distcmd = self.distcmd
        infoflags = self.infoflags
        distflags = self.distflags
        uploadflags = self.uploadflags
        scmtype = self.scm.name

        try:
            if self.isremote:
                directory = join(tempdir, 'checkout')
                self.scm.checkout_url(self.remoteurl, directory)
            else:
                directory = abspath(expanduser(self.directory))

            self.scm.check_valid_sandbox(directory)
            self.setuptools.check_valid_package(directory)

            if self.isremote or not (self.skipcheckin and self.skiptag):
                self.scm.check_dirty_sandbox(directory)
                self.scm.check_unclean_sandbox(directory)

            name, version = self.setuptools.get_package_info(directory)
            if self.isremote:
                print 'Releasing', name, version

            if not self.skiptag:
                tagid = self.scm.make_tagid(directory, version)
                self.scm.check_tag_exists(directory, tagid)
                print 'Tagging', name, version
                self.scm.create_tag(directory, tagid, name, version, self.push)

            distfile = self.setuptools.run_dist(
                directory, distcmd, infoflags, distflags, scmtype, self.quiet)

            if not self.skipupload:
                for location in self.locations:
                    if self.locations.is_server(location):
                        if '--sign' in uploadflags and isfile(distfile+'.asc'):
                            os.remove(distfile+'.asc')
                        self.setuptools.run_upload(
                            directory, location, distcmd, infoflags, distflags, uploadflags, scmtype)
                    else:
                        self.scp.run_scp(distfile, location)
        finally:
            shutil.rmtree(tempdir)

    def run(self):
        self.get_python()
        self.get_options()
        self.get_package()
        self.make_release()
        print 'done'


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    try:
        ReleaseMaker(args).run()
    except SystemExit, e:
        return e.code
    return 0


if __name__ == '__main__':
    sys.exit(main())

