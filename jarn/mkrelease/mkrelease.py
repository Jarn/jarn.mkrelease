import sys
import os
import getopt
import tempfile
import shutil

from os.path import abspath, join, exists, isdir, isfile

python = "python2.4"
distbase = "jarn.com:/home/psol/dist"
distdefault = "public"

version = "mkrelease 0.14"
usage = """\
Usage: mkrelease [-CTSDK] [-z] [-d dist-location] [svn-url|svn-sandbox]
       mkrelease [-CTSDK] [-z] [-p [-s [-i identity]]] [svn-url|svn-sandbox]

Release an sdist egg.

Options:
  -C                Do not checkin release-relevant files from the sandbox.
  -T                Do not tag the release in subversion.
  -S                Do not scp the release tarball to dist-location.
  -D                Dry-run; equivalent to -CTS.
  -K                Keep the temporary build directory.

  -z                Create .zip archive instead of the default .tar.gz.

  -d dist-location  A full scp destination specification.
                    There is a shortcut for Jarn use: If the location does not
                    contain a host part, %(distbase)s is prepended.
                    Defaults to %(distdefault)s (%(distbase)s/%(distdefault)s).

  -p                Upload the release to PyPI.
  -s                Sign the release tarball with GnuPG.
  -i identity       The GnuPG identity to sign with.

  svn-url           A URL with protocol svn, svn+ssh, http, https, or file.
  svn-sandbox       A local directory; defaults to the current working
                    directory.

Examples:
  mkrelease -d nordic https://svn.jarn.com/customers/nordic/nordic.theme/trunk

  mkrelease -d nordic src/nordic.theme

  cd src/jarn.somepackage
  mkrelease
""" % locals()


def system(cmd):
    return os.system(cmd)


def pipe(cmd):
    p = os.popen(cmd)
    try:
        return p.readline()[:-1]
    finally:
        p.close()


def find(dir, regex, maxdepth=1000):
    return pipe("find %(dir)s -maxdepth %(maxdepth)s -iregex '%(regex)s' -print" % locals())


class ReleaseMaker(object):

    def __init__(self):
        self.skipcheckin = False
        self.skiptag = False
        self.skipscp = False
        self.keeptemp = False
        self.pypi = False
        self.distlocation = "%s/%s" % (distbase, distdefault)
        self.directory = os.curdir
        self.python = python
        self.sdistflags = []
        self.uploadflags = []

    def err_exit(self, msg, rc=1):
        print >>sys.stderr, msg
        sys.exit(rc)

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
        if system('svn ls "%(url)s" 2>/dev/null' % locals()) == 0:
            self.err_exit('Tag exists: %(url)s' % locals())

    def make_tagurl(self, url, tag):
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
        return (location.find(':') > 0)

    def get_options(self):
        try:
            options, args = getopt.getopt(sys.argv[1:], "CDKSTd:hi:psvz")
        except getopt.GetoptError, e:
            self.err_exit('%s\n\n%s' % (e.msg, usage))

        for name, value in options:
            name = name[1:]
            if name == 'C':
                self.skipcheckin = True
            elif name == 'T':
                self.skiptag = True
            elif name == 'S':
                self.skipscp = True
            elif name == 'D':
                self.skipcheckin = self.skiptag = self.skipscp = True
            elif name == 'K':
                self.keeptemp = True
            elif name == 'z':
                self.sdistflags.append('--formats=zip')
            elif name == 'd':
                self.distlocation = value
                if not self.has_host(value):
                    self.distlocation = '%s/%s' % (distbase, value)
            elif name == 'p':
                self.pypi = True
            elif name == 's':
                self.uploadflags.append('--sign')
            elif name == 'i':
                self.uploadflags.append('--identity=%s' % value)
            elif name == 'v':
                self.err_exit(version, 0)
            elif name == 'h':
                self.err_exit(usage, 0)
            else:
                self.err_exit(usage)

        if args:
            self.directory = args[0]

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

            name = pipe("%(python)s setup.py --name" % locals())
            version = pipe("%(python)s setup.py --version" % locals())

            print 'Releasing', name, version
            print 'URL:', self.trunkurl

            if not self.skipcheckin:
                setup_cfg = find(directory, r'.*[/\\:]setup\.cfg$', maxdepth=1)
                changes_txt = find(directory, r'.*[/\\:]CHANGES\.txt$')
                history_txt = find(directory, r'.*[/\\:]HISTORY\.txt$')
                version_txt = find(directory, r'.*[/\\:]version\.txt$')
                rc = system('svn ci -m"Prepare %(name)s %(version)s." setup.py %(setup_cfg)s '
                            '%(changes_txt)s %(history_txt)s %(version_txt)s' % locals())
                if rc != 0:
                    self.err_exit('Checkin failed')

    def make_release(self):
        tempname = tempfile.mkdtemp(prefix='release')
        checkout = join(tempname, 'checkout')
        trunkurl = self.trunkurl
        distlocation = self.distlocation
        python = self.python
        sdistflags = ' '.join(self.sdistflags)
        uploadflags = ' '.join(self.uploadflags)

        try:
            rc = system('svn co "%(trunkurl)s" "%(checkout)s"' % locals())
            if rc != 0:
                self.err_exit('Checkout failed')

            self.assert_package(checkout)
            os.chdir(checkout)
            name = pipe("%(python)s setup.py --name" % locals())
            version = pipe("%(python)s setup.py --version" % locals())

            print 'Releasing', name, version

            if not self.skiptag:
                tagurl = self.make_tagurl(trunkurl, version)
                self.assert_tagurl(tagurl)
                rc = system('svn cp -m"Tagged %(name)s %(version)s." "%(trunkurl)s" "%(tagurl)s"' % locals())
                if rc != 0:
                    self.err_exit('Tag failed')

            if not self.skipscp and self.pypi:
                rc = system('"%(python)s" setup.py sdist %(sdistflags)s register upload %(uploadflags)s' % locals())
            else:
                rc = system('"%(python)s" setup.py sdist %(sdistflags)s' % locals())
                if not self.skipscp and rc == 0:
                    rc = system('scp dist/* "%(distlocation)s"' % locals())

            if rc != 0:
                self.err_exit('Release failed')
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

