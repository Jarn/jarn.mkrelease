import sys
import os
import getopt
import tempfile
import shutil

from os.path import abspath, join, exists, isdir, isfile

python = "python2.4"
distbase = "jarn.com:/home/psol/dist"
distdefault = "public"

usage = """Usage: mkrelease [-CTSDK] [-d dist-location] [svn-url|svn-sandbox]

Release an sdist egg.

Options:
  -C                Do not checkin CHANGES.txt and setup.py.
  -T                Do not tag the release in subversion.
  -S                Do not scp the release tarball to dist-location.
  -D                Dry-run; equivalent to -CTS.
  -K                Keep the temporary build directory.

  -d dist-location  A full scp destination specification.
                    There is a shortcut for Jarn use: If the location does not
                    contain a host part, %(distbase)s is prepended.
                    Defaults to %(distdefault)s (%(distbase)s/%(distdefault)s).

  svn-url           A URL with protocol svn, svn+ssh, http, https, or file.
  svn-sandbox       A local directory; defaults to the current working directory.

Examples:
  mkrelease -d nordic https://svn.jarn.com/customers/nordic/nordic.content/trunk

  mkrelease -d nordic src/nordic.content

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


class ReleaseMaker(object):

    def __init__(self):
        self.dryrun = False
        self.skipcheckin = False
        self.skiptag = False
        self.skipscp = False
        self.keeptemp = False
        self.distlocation = "%s/%s" % (distbase, distdefault)
        self.directory = "."

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
        if not url.endswith('/trunk'):
            self.err_exit("URL must point to trunk: %(url)s" % locals())

    def assert_tagurl(self, url):
        if system('svn ls "%(url)s" 2>/dev/null' % locals()) == 0:
            self.err_exit('Tag exists: %(url)s' % locals())

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
            options, args = getopt.getopt(sys.argv[1:], "CDKSTd:h")
        except getopt.GetoptError, e:
            self.err_exit('%s\n\n%s' % (e.msg.capitalize(), usage))

        for name, value in options:
            name = name[1:]
            if name == 'D':
                self.dryrun = True
            elif name == 'C':
                self.skipcheckin = True
            elif name == 'T':
                self.skiptag = True
            elif name == 'S':
                self.skipscp = True
            elif name == 'K':
                self.keeptemp = True
            elif name == 'd':
                self.distlocation = value
                if not self.has_host(value):
                    self.distlocation = '%s/%s' % (distbase, value)
            elif name == 'h':
                self.err_exit(usage, 0)
            else:
                self.err_exit(usage)

        if self.dryrun:
            self.skipcheckin = self.skiptag = self.skipscp = True

        if args:
            self.directory = args[0]

    def get_package_url(self):
        if self.is_svnurl(self.directory):
            self.trunkurl = self.directory
            self.assert_trunkurl(self.trunkurl)
        else:
            self.directory = abspath(self.directory)
            self.assert_checkout(self.directory)
            self.assert_package(self.directory)
            os.chdir(self.directory)
            self.trunkurl = pipe("svn info | grep ^URL")[5:]
            self.assert_trunkurl(self.trunkurl)

            name = pipe("%(python)s setup.py --name" % dict(python=python))
            version = pipe("%(python)s setup.py --version" % dict(python=python))

            print 'Releasing', name, version
            print self.trunkurl

            if not self.skipcheckin:
                system('svn ci -m"Prepare %(name)s %(version)s." CHANGES.txt setup.py' % locals())

    def make_release(self):
        tempname = tempfile.mkdtemp(prefix='release')
        checkout = join(tempname, 'checkout')
        trunkurl = self.trunkurl
        distlocation = self.distlocation
        try:
            system('svn export "%(trunkurl)s" "%(checkout)s"' % locals())

            self.assert_package(checkout)
            os.chdir(checkout)
            name = pipe("%(python)s setup.py --name" % dict(python=python))
            version = pipe("%(python)s setup.py --version" % dict(python=python))

            print 'Releasing', name, version

            tagurl = '%s/tags/%s' % (trunkurl.rsplit('/', 1)[0], version)
            if not self.skiptag:
                self.assert_tagurl(tagurl)
                system('svn cp -m"Tagged %(name)s %(version)s." "%(trunkurl)s" "%(tagurl)s"' % locals())

            rc = system('"%(python)s" setup.py sdist' % dict(python=python))
            if not self.skipscp and rc == 0:
                system('scp dist/* "%(distlocation)s"' % locals())
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

