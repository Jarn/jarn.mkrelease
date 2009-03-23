import sys
import os
import getopt
import tempfile
import shutil
import ConfigParser

from subprocess import Popen, PIPE
from os.path import abspath, join, exists, isdir, isfile, expanduser

python = "python2.6"
distbase = ""
distdefault = ""
maxaliasdepth = 23

version = "mkrelease 1.0b3"
usage = """\
Usage: mkrelease [options] [svn-url|svn-sandbox]

Release an sdist egg.

Options:
  -C                Do not checkin modified files from the sandbox.
  -T                Do not tag the release in subversion.
  -S                Do not scp the release tarball to dist-location.
  -D                Dry-run; equivalent to -CTS.
  -K                Keep the temporary build directory.

  -s                Sign the release tarball with GnuPG.
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
    p = Popen(cmd, shell=True)
    p.communicate()
    return p.returncode


def raw_pipe(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    stdout = p.communicate()[0]
    if p.returncode == 0:
        return stdout.replace('\r','\n').split('\n')
    return []


def pipe(cmd):
    lines = raw_pipe(cmd)
    if lines:
        return lines[0]
    return ''


class Defaults(object):

    def __init__(self):
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

    def __init__(self):
        self.defaults = Defaults()
        self.skipcheckin = False
        self.skiptag = False
        self.skipscp = False
        self.keeptemp = False
        self.distlocation = []
        self.sdistflags = ['--formats=zip']
        self.uploadflags = []
        self.directory = os.curdir
        self.python = self.defaults.python
        self.distbase = self.defaults.distbase
        self.distdefault = self.defaults.distdefault
        self.aliases = self.defaults.aliases
        self.servers = self.defaults.servers

    def err_exit(self, msg, rc=1):
        print >>sys.stderr, msg
        sys.exit(rc)

    def is_svnurl(self, url):
        return (url.startswith('svn://') or
                url.startswith('svn+ssh://') or
                url.startswith('http://') or
                url.startswith('https://') or
                url.startswith('file://'))

    def has_host(self, location):
        colon = location.find(':')
        slash = location.find('/')
        return colon > 0 and (slash < 0 or slash > colon)

    def assert_checkout(self, dir):
        if not exists(dir):
            self.err_exit("No such file or directory: %(dir)s" % locals())
        if not isdir(dir):
            self.err_exit("Not a directory: %(dir)s" % locals())
        if not isdir(join(dir, '.svn')):
            self.err_exit("Not a checkout: %(dir)s" % locals())

    def assert_package(self, dir):
        if not exists(dir):
            self.err_exit("No such file or directory: %(dir)s" % locals())
        if not isdir(dir):
            self.err_exit("Not a directory: %(dir)s" % locals())
        if not isfile(join(dir, 'setup.py')):
            self.err_exit("Not eggified (no setup.py found): %(dir)s" % locals())

    def assert_tagurl(self, url):
        devnull = os.devnull
        if system('svn ls "%(url)s" >%(devnull)s 2>&1' % locals()) == 0:
            self.err_exit("Tag exists: %(url)s" % locals())

    def get_trunkurl(self, dir):
        lines = raw_pipe('svn info "%(dir)s"' % locals())
        if not lines:
            self.err_exit('Svn info failed')
        url = lines[1][5:]
        if not self.is_svnurl(url):
            self.err_exit('Bad URL: %(url)s' % locals())
        return url

    def get_tagurl(self, url, tag):
        parts = url.split('/')
        if parts[-1] == 'trunk':
            parts = parts[:-1]
        elif parts[-2] in ('branches', 'tags'):
            parts = parts[:-2]
        else:
            self.err_exit("URL must point to trunk, branch, or tag: %(url)s" % locals())
        return '/'.join(parts + ['tags', tag])

    def assert_location(self, locations):
        if not locations:
            self.err_exit('mkrelease: option -d is required\n\n%s' % usage)
        for location in locations:
            if location not in self.servers and not self.has_host(location):
                self.err_exit('Scp destination must contain host part: %(location)s' % locals())

    def get_location(self, location, depth=0):
        if not location:
            return []
        if location in self.aliases:
            res = []
            if depth > maxaliasdepth:
                self.err_exit('Maximum alias recursion depth exceeded: %(location)s' % locals())
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
        try:
            options, args = getopt.getopt(sys.argv[1:], 'CDKSTd:hi:sv',
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

    def get_package_url(self):
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

            print 'Releasing', name, version
            print 'URL:', self.trunkurl

            if not self.skipcheckin:
                rc = system('svn ci -m"Prepare %(name)s %(version)s."' % locals())
                if rc != 0:
                    self.err_exit('Checkin failed')

    def make_release(self):
        tempname = abspath(tempfile.mkdtemp(prefix='release-'))
        trunkurl = self.trunkurl
        python = self.python
        register = 'register'
        upload = 'upload'
        sdistflags = ' '.join(self.sdistflags)
        uploadflags = ' '.join(self.uploadflags)

        if pipe('"%(python)s" -c"import sys; print sys.version[:3]"' % locals()) < '2.6':
            register, upload = 'mregister', 'mupload'

        try:
            rc = system('svn co "%(trunkurl)s" "%(tempname)s"' % locals())
            if rc != 0:
                self.err_exit('Checkout failed')

            self.assert_package(tempname)
            os.chdir(tempname)
            name = pipe('"%(python)s" setup.py --name' % locals())
            version = pipe('"%(python)s" setup.py --version' % locals())

            print 'Releasing', name, version

            if not self.skiptag:
                tagurl = self.get_tagurl(trunkurl, version)
                self.assert_tagurl(tagurl)
                rc = system('svn cp -m"Tagged %(name)s %(version)s." "%(trunkurl)s" "%(tagurl)s"' % locals())
                if rc != 0:
                    self.err_exit('Tag failed')

            rc = system('"%(python)s" setup.py sdist %(sdistflags)s' % locals())
            if rc != 0:
                self.err_exit('Release failed')

            if not self.skipscp:
                for location in self.distlocation:
                    if location in self.servers:
                        serverflags = '--repository="%s"' % location
                        rc = system('"%(python)s" setup.py sdist %(sdistflags)s %(register)s %(serverflags)s '
                                    '%(upload)s %(uploadflags)s %(serverflags)s' % locals())
                        if rc != 0:
                            self.err_exit('Upload failed')
                    else:
                        rc = system('scp dist/* "%(location)s"' % locals())
                        if rc != 0:
                            self.err_exit('Scp failed')
        finally:
            if not self.keeptemp:
                shutil.rmtree(tempname)

    def run(self):
        self.get_options()
        self.get_package_url()
        self.make_release()
        print 'done'


def main():
    ReleaseMaker().run()
    sys.exit(0)


if __name__ == '__main__':
    main()

