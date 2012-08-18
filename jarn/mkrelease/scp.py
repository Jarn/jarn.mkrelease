import tempfile
import tee

from process import Process
from exit import err_exit


class SCP(object):
    """Secure copy and FTP abstraction."""

    def __init__(self, process=None):
        self.process = process or Process()

    def run_scp(self, distfile, location):
        if not self.process.quiet:
            print 'scp-ing to %(location)s' % locals()
        rc = self.process.os_system(
            'scp "%(distfile)s" "%(location)s"' % locals())
        if rc != 0:
            err_exit('scp failed')
        return rc

    def run_sftp(self, distfile, location):
        if not self.process.quiet:
            print 'sftp-ing to %(location)s' % locals()
        with tempfile.NamedTemporaryFile(prefix='sftp-') as file:
            file.write('put "%(distfile)s"\n' % locals())
            file.write('quit\n')
            file.flush()
            cmdfile = file.name
            rc, lines = self.process.popen(
                'sftp -b "%(cmdfile)s" "%(location)s"' % locals(),
                echo=tee.StartsWith('Uploading'))
            if rc != 0:
                err_exit('sftp failed')
            return rc

