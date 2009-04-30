import sys
import os
import getopt
import tempfile
import shutil
import ConfigParser

from os.path import abspath, join, expanduser, exists, isdir, isfile
from tee import popen, pipe, NotEmpty, NotBefore

python = "python2.6"
distbase = ""
distdefault = ""
maxaliasdepth = 23

version = "mkrelease 1.0b4"
usage = """\
Usage: mkrelease [options] [svn-url|svn-sandbox]

Release an sdist egg.

Options:
  -C                Do not checkin modified files from the sandbox.
  -T                Do not tag the release in subversion.
  -S                Do not scp the release to dist-location.
  -D                Dry-run; equivalent to -CTS.
  -K                Keep the temporary build directory.

  -s                Sign the release with GnuPG.
  -i identity       The GnuPG identity to sign with.

  -d dist-location  An scp destination specification, or an index server
                    configured in ~/.pypirc, or an alias name for either.
                    This option may be specified more than once.

  svn-url           A URL with protocol svn, svn+ssh, http, https, or file.
  svn-sandbox       A local directory; defaults to the current working
                    directory.

Files:
  /etc/mkrelease    Global configuration file.
  ~/.mkrelease      Per user configuration file.

  The configuration file consists of sections, led by a "[section]" header
  and followed by "name = value" entries.

  The [defaults] section has the following options:

  python            The Python executable used; defaults to %(python)s.
  distbase          The value prepended if dist-location does not contain a
                    host part. Applies to scp dist-locations only.
  distdefault       The default value for dist-location.

  The [aliases] section may be used to define short names for (one or more)
  dist-locations.
""" % locals()


def system(cmd):
    """Run cmd and return its exit code.
    """
    rc, lines = popen(cmd, echo=NotEmpty())
    return rc


def run_sdist(cmd):
    """Run 'setup.py sdist' and check its results.

    Returns 0 on success, 1 on failure.
    """
    rc, lines = popen(cmd)
    if rc == 0 and isdir('dist') and os.listdir('dist'):
        return 0
    return 1


def run_upload(cmd):
    """Run 'setup.py register upload' and check its results.

    Returns 0 on success, 1 on failure.
    """
    rc, lines = popen(cmd, echo=NotBefore('running register'))
    register_ok = upload_ok = False
    current, expect = None, 'running register'
    for line in lines:
        if line == expect:
            if line == 'Server response (200): OK':
                if current == 'running register':
                    register_ok = True
                    current, expect = expect, 'running upload'
                elif current == 'running upload':
                    upload_ok = True
                    current, expect = expect, None
            else:
                current, expect = expect, 'Server response (200): OK'
    if rc == 0 and register_ok and upload_ok:
        return 0
    return 1


def run_scp(cmd):
    """Run scp and return its exit code.
    """
    # Scp output cannot be tee'd
    return os.system(cmd)


class Defaults(object):

    def __init__(self):
        """Read config files.
        """
        self.parser = ConfigParser.ConfigParser()
        self.parser.read((expanduser('~/.pypirc'), '/etc/mkrelease',
                          expanduser('~/.mkrelease')))

        def get(section, key, default=None):
            if self.parser.has_option(section, key):
                return self.parser.get(section, key)
            return default

        self.python = get('defaults', 'python', python)
        self.distbase = get('defaults', 'distbase', distbase)
        self.distdefault = get('defaults', 'distdefault', distdefault)

        self.aliases = {}
        if self.parser.has_section('aliases'):
            for key, value in self.parser.items('aliases'):
                self.aliases[key] = value.split()

        self.servers = {}
        for server in get('distutils', 'index-servers', '').split():
            self.servers[server] = True
            url = get(server, 'repository')
            if url is not None:
                self.servers[url] = True


class ReleaseMaker(object):

    def __init__(self, args):
        """Set defaults.
        """
        defaults = Defaults()
        self.skipcheckin = False
        self.skiptag = False
        self.skipscp = False
        self.keeptemp = False
        self.distlocation = []
        self.sdistflags = ['--formats="zip"']
        self.uploadflags = []
        self.directory = os.curdir
        self.python = defaults.python
        self.distbase = defaults.distbase
        self.distdefault = defaults.distdefault
        self.aliases = defaults.aliases
        self.servers = defaults.servers
        self.args = args

    def err_exit(self, msg, rc=1):
        """Print msg to stderr and exit with rc.
        """
        print >>sys.stderr, msg
        sys.exit(rc)

    def is_svnurl(self, url):
        """Return True if 'url' appears to be an SVN URL.
        """
        return (url.startswith('svn://') or
                url.startswith('svn+ssh://') or
                url.startswith('http://') or
                url.startswith('https://') or
                url.startswith('file://'))

    def has_host(self, location):
        """Return True if 'location' contains a host part.
        """
        colon = location.find(':')
        slash = location.find('/')
        return colon > 0 and (slash < 0 or slash > colon)

    def assert_checkout(self, dir):
        """Fail if 'dir' is not an SVN checkout.
        """
        if not exists(dir):
            self.err_exit("No such file or directory: %(dir)s" % locals())
        if not isdir(dir):
            self.err_exit("Not a directory: %(dir)s" % locals())
        if not isdir(join(dir, '.svn')):
            self.err_exit("Not a checkout: %(dir)s" % locals())

    def assert_package(self, dir):
        """Fail if 'dir' is not eggified.
        """
        if not exists(dir):
            self.err_exit("No such file or directory: %(dir)s" % locals())
        if not isdir(dir):
            self.err_exit("Not a directory: %(dir)s" % locals())
        if not isfile(join(dir, 'setup.py')):
            self.err_exit("Not eggified (no setup.py found): %(dir)s" % locals())

    def get_trunkurl(self, dir):
        """Get the repository URL from the SVN sandbox in 'dir'.
        """
        rc, lines = popen('svn info "%(dir)s"' % locals(), echo=False)
        if rc != 0 or not lines:
            self.err_exit('Svn info failed')
        url = lines[1][5:]
        if not self.is_svnurl(url):
            self.err_exit('Bad URL: %(url)s' % locals())
        return url

    def assert_tagurl(self, url):
        """Fail if tag 'url' exists.
        """
        rc, lines = popen('svn ls "%(url)s"' % locals(), echo=False, echo2=False)
        if rc == 0:
            self.err_exit("Tag exists: %(url)s" % locals())

    def get_tagurl(self, url, tag):
        """Construct the tag URL.
        """
        parts = url.split('/')
        if parts[-1] == 'trunk':
            parts = parts[:-1]
        elif parts[-2] in ('branches', 'tags'):
            parts = parts[:-2]
        else:
            self.err_exit("URL must point to trunk, branch, or tag: %(url)s" % locals())
        return '/'.join(parts + ['tags', tag])

    def assert_location(self, locations):
        """Fail if 'locations' is empty or contains bad scp destinations.
        """
        if not locations:
            self.err_exit('mkrelease: option -d is required\n\n%s' % usage)
        for location in locations:
            if location not in self.servers and not self.has_host(location):
                self.err_exit('Scp destination must contain host part: %(location)s' % locals())

    def get_location(self, location, depth=0):
        """Resolve aliases and apply distbase.
        """
        if not location:
            return []
        if location in self.aliases:
            res = []
            if depth > maxaliasdepth:
                self.err_exit('Maximum alias depth exceeded: %(location)s' % locals())
            for loc in self.aliases[location]:
                res.extend(self.get_location(loc, depth+1))
            return res
        if location in self.servers:
            return [location]
        if not self.has_host(location) and self.distbase:
            sep = '/'
            if self.distbase[-1] in (':', '/'):
                sep = ''
            return [self.distbase + sep + location]
        return [location]

    def get_options(self):
        """Parse command line.
        """
        try:
            options, args = getopt.getopt(self.args, 'CDKSTd:hi:sv',
                ('skip-checkin', 'skip-tag', 'skip-scp', 'dry-run', 'keep-temp',
                 'sign', 'identity=', 'dist-location=', 'version', 'help'))
        except getopt.GetoptError, e:
            self.err_exit('mkrelease: %s\n\n%s' % (e.msg, usage))

        for name, value in options:
            if name in ('-C', '--skip-checkin'):
                self.skipcheckin = True
            elif name in ('-T', '--skip-tag'):
                self.skiptag = True
            elif name in ('-S', '--skip-scp'):
                self.skipscp = True
            elif name in ('-D', '--dry-run'):
                self.skipcheckin = self.skiptag = self.skipscp = True
            elif name in ('-K', '--keep-temp'):
                self.keeptemp = True
            elif name in ('-s', '--sign'):
                self.uploadflags.append('--sign')
            elif name in ('-i', '--identity'):
                self.uploadflags.append('--identity="%s"' % value)
            elif name in ('-d', '--dist-location'):
                self.distlocation.extend(self.get_location(value))
            elif name in ('-v', '--version'):
                self.err_exit(version, 0)
            elif name in ('-h', '--help'):
                self.err_exit(usage, 0)

        if not self.distlocation:
            self.distlocation = self.get_location(self.distdefault)

        if not self.skipscp:
            self.assert_location(self.distlocation)

        if len(args) > 1:
            self.err_exit('mkrelease: too many arguments\n\n%s' % usage)

        if args:
            self.directory = args[0]

    def get_pythonversion(self):
        """Get version of configured Python interpreter.
        """
        python = self.python

        self.pythonversion = pipe('"%(python)s" -c"import sys; print sys.version[:3]"' % locals())
        if not self.pythonversion:
            self.err_exit('Bad interpreter')

    def get_packageurl(self):
        """Get URL to release.
        """
        directory = self.directory
        python = self.python

        if self.is_svnurl(directory):
            self.trunkurl = directory
        else:
            directory = abspath(directory)
            self.assert_checkout(directory)
            self.assert_package(directory)
            self.trunkurl = self.get_trunkurl(directory)

            os.chdir(directory)
            name = pipe('"%(python)s" setup.py --name' % locals())
            version = pipe('"%(python)s" setup.py --version' % locals())

            if not name or not version:
                self.err_exit('Bad setup.py')

            print 'Releasing', name, version
            print 'URL:', self.trunkurl

            if not self.skipcheckin:
                rc = system('svn ci -m"Prepare %(name)s %(version)s."' % locals())
                if rc != 0:
                    self.err_exit('Checkin failed')

    def get_uploadcmds(self):
        """Get register and upload commands.
        """
        if self.pythonversion < '2.6':
            self.register = 'mregister'
            self.upload = 'mupload'
        else:
            self.register = 'register'
            self.upload = 'upload'

    def make_release(self):
        """Build and distribute the egg.
        """
        tempname = abspath(tempfile.mkdtemp(prefix='release-'))
        trunkurl = self.trunkurl
        python = self.python
        register = self.register
        upload = self.upload
        sdistflags = ' '.join(self.sdistflags)
        uploadflags = ' '.join(self.uploadflags)

        try:
            rc = system('svn co "%(trunkurl)s" "%(tempname)s"' % locals())
            if rc != 0:
                self.err_exit('Checkout failed')

            self.assert_package(tempname)
            os.chdir(tempname)
            name = pipe('"%(python)s" setup.py --name' % locals())
            version = pipe('"%(python)s" setup.py --version' % locals())

            if not name or not version:
                self.err_exit('Bad setup.py')

            print 'Releasing', name, version

            if not self.skiptag:
                tagurl = self.get_tagurl(trunkurl, version)
                self.assert_tagurl(tagurl)
                rc = system('svn cp -m"Tagged %(name)s %(version)s." '
                            '"%(trunkurl)s" "%(tagurl)s"' % locals())
                if rc != 0:
                    self.err_exit('Tag failed')

            rc = run_sdist('"%(python)s" setup.py sdist %(sdistflags)s' % locals())
            if rc != 0:
                self.err_exit('Release failed')

            if not self.skipscp:
                for location in self.distlocation:
                    if location in self.servers:
                        serverflags = '--repository="%s"' % location
                        rc = run_upload('"%(python)s" setup.py sdist %(sdistflags)s '
                                        '%(register)s %(serverflags)s '
                                        '%(upload)s %(uploadflags)s %(serverflags)s' % locals())
                        if rc != 0:
                            self.err_exit('Upload failed')
                    else:
                        rc = run_scp('scp dist/* "%(location)s"' % locals())
                        if rc != 0:
                            self.err_exit('Scp failed')
        finally:
            if not self.keeptemp:
                shutil.rmtree(tempname)

    def run(self):
        self.get_options()
        self.get_pythonversion()
        self.get_packageurl()
        self.get_uploadcmds()
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

