import tempfile
import time
import tee

from os.path import split

from process import Process
from chdir import ChdirStack
from exit import err_exit


class SCP(object):
    """Secure copy and FTP abstraction."""

    def __init__(self, process=None):
        self.process = process or Process()

    def run_scp(self, distfile, location, quiet=False):
        if not self.process.quiet:
            print 'running scp'
            time.sleep(0.4)
            dir, basename = split(distfile)
            print 'Uploading dist/%(basename)s to %(location)s' % locals()

        rc, lines = self.process.popen(
            'scp "%(distfile)s" "%(location)s"' % locals(),
            echo=False)
        if rc != 0:
            err_exit('scp failed')
        if not self.process.quiet and not quiet:
            print 'OK'
        return rc

    def run_sftp(self, distfile, location, quiet=False):
        if not self.process.quiet:
            print 'running sftp'
            time.sleep(0.3)
            dir, basename = split(distfile)
            print 'Uploading dist/%(basename)s to %(location)s' % locals()

        with tempfile.NamedTemporaryFile(prefix='sftp-') as file:
            file.write('put "%(distfile)s"\n' % locals())
            file.write('bye\n')
            file.flush()
            cmdfile = file.name
            rc, lines = self.process.popen(
                'sftp -b "%(cmdfile)s" "%(location)s"' % locals(),
                echo=False)

        if rc != 0:
            err_exit('sftp failed')
        if not self.process.quiet and not quiet:
            print 'OK'
        return rc

