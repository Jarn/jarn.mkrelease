import sys
import os
import getopt
import tempfile
import shutil
import ConfigParser

from os.path import abspath, join, exists, isdir, isfile, expanduser

python = "python2.6"
distbase = ""
distdefault = ""

version = "mkrelease 0.20"
usage = """\
Usage: mkrelease [options] [svn-url|svn-sandbox]

Release an sdist egg.

Options:
  -C                Do not checkin release-relevant files from the sandbox.
  -T                Do not tag the release in subversion.
  -S                Do not scp the release tarball to dist-location.
  -D                Dry-run; equivalent to -CTS.
  -K                Keep the temporary build directory.

  -z                Create a zip archive instead of the default tar.gz.
  -s                Sign the release tarball with GnuPG.
  -i identity       The GnuPG identity to sign with.

  -d dist-location  An scp destination specification, or an index server
                    configured in ~/.pypirc, or an alias name for either.

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
    return os.system(cmd)


def pipe(cmd):
    p = os.popen(cmd)
    try:
        return p.readline()[:-1]
    finally:
        p.close()


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
        self.sdistflags = []
        self.uploadflags = []
        self.directory = os.curdir
        self.python = self.defaults.python
        self.distbase = self.defaults.distbase
        self.distdefault = self.defaults.distdefault
        self.aliases = self.defaults.aliases
        self.servers = self.defaults.servers
        self.distlocation = self.get_location(self.distdefault)

    def err_exit(self, msg, rc=1):
        print >>sys.stderr, msg
        sys.exit(rc)

    def assert_location(self, locations):
        if not locations:
            self.err_exit('option -d is required\n\n%s' % usage)
        for location in locations:
            if location not in self.servers and not self.has_host(location):
                self.err_exit('scp destination must contain a host part: '
                              '%s\n\n%s' % (location, usage))

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

    def assert_trunkurl(self, url):
        parts = url.split('/')
        if parts[-1] != 'trunk' and parts[-2] not in ('branches', 'tags'):
            self.err_exit("URL must point to trunk, branch, or tag: %(url)s" % locals())

    def assert_tagurl(self, url):
        devnull = os.devnull
        if system('svn ls "%(url)s" >%(devnull)s 2>&1' % locals()) == 0:
            self.err_exit("Tag exists: %(url)s" % locals())

    def get_location(self, location):
        if not location:
            return []
        if location in self.aliases:
            return self.aliases[location]
        if location in self.servers:
            return [location]
        if not self.has_host(location) and self.distbase:
            return [self.join(self.distbase, location)]
        return [location]

    def get_tagurl(self, url, tag):
        parts = url.split('/')
        if parts[-1] == 'trunk':
            parts = parts[:-1]
        elif parts[-2] in ('branches', 'tags'):
            parts = parts[:-2]
        return '/'.join(parts + ['tags', tag])

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

    def join(self, base, location):
        sep = '/'
        if base[-1] in ('/', ':'):
            sep = ''
        return '%s%s%s' % (base, sep, location)

    def find(self, dir, name, maxdepth=999):
        regex = r'.*[/\\:]%s$' % name.replace('.', '[.]')
        return pipe('find "%(dir)s" -maxdepth %(maxdepth)s -iregex "%(regex)s" -print' % locals())

    def get_options(self):
        try:
            options, args = getopt.getopt(sys.argv[1:], 'CDKSTd:hi:svz', ('help', 'version'))
        except getopt.GetoptError, e:
            self.err_exit('%s\n\n%s' % (e.msg, usage))

        for name, value in options:
            if name == '-C':
                self.skipcheckin = True
            elif name == '-T':
                self.skiptag = True
            elif name == '-S':
                self.skipscp = True
            elif name == '-D':
                self.skipcheckin = self.skiptag = self.skipscp = True
            elif name == '-K':
                self.keeptemp = True
            elif name == '-z':
                self.sdistflags.append('--formats=zip')
            elif name == '-s':
                self.uploadflags.append('--sign')
            elif name == '-i':
                self.uploadflags.append('--identity=%s' % value)
            elif name == '-d':
                self.distlocation = self.get_location(value)
            elif name in ('-v', '--version'):
                self.err_exit(version, 0)
            elif name in ('-h', '--help'):
                self.err_exit(usage, 0)
            else:
                self.err_exit(usage)

        if args:
            self.directory = args[0]

        if not self.skipscp:
            self.assert_location(self.distlocation)

    def get_package_url(self):
        directory = self.directory
        python = self.python

        if self.is_svnurl(directory):
            self.trunkurl = directory
            self.assert_trunkurl(self.trunkurl)
        else:
            directory = abspath(directory)
            self.assert_checkout(directory)
            self.assert_package(directory)
            os.chdir(directory)
            self.trunkurl = pipe("svn info | grep ^URL")[5:]
            self.assert_trunkurl(self.trunkurl)

            name = pipe('"%(python)s" setup.py --name' % locals())
            version = pipe('"%(python)s" setup.py --version' % locals())

            print 'Releasing', name, version
            print 'URL:', self.trunkurl

            if not self.skipcheckin:
                setup_cfg = self.find(directory, 'setup.cfg', maxdepth=1)
                changes_txt = self.find(directory, 'CHANGES.txt')
                history_txt = self.find(directory, 'HISTORY.txt')
                version_txt = self.find(directory, 'version.txt')
                rc = system('svn ci -m"Prepare %(name)s %(version)s." setup.py "%(setup_cfg)s" '
                            '"%(changes_txt)s" "%(history_txt)s" "%(version_txt)s"' % locals())
                if rc != 0:
                    self.err_exit('Checkin failed')

    def make_release(self):
        tempname = abspath(tempfile.mkdtemp(prefix='release-'))
        trunkurl = self.trunkurl
        python = self.python
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
                        serverflags = '--repository=%s' % location
                        rc = system('"%(python)s" setup.py sdist %(sdistflags)s register %(serverflags)s '
                                    'upload %(uploadflags)s %(serverflags)s' % locals())
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

