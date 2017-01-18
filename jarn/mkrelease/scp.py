from __future__ import absolute_import
from __future__ import print_function

import sys
import tempfile
import time
import random

from os.path import basename

from .process import Process
from .exit import err_exit
from .utils import encode


class SCP(object):
    """Secure copy and FTP abstraction."""

    def __init__(self, process=None):
        self.process = process or Process()

    def delay(self):
        # Reduce output jerkiness
        time.sleep(random.choice([0.3, 0.4]))

    def run_upload(self, scheme, distfile, location):
        if scheme == 'sftp':
            return self.run_sftp(distfile, location)
        else:
            return self.run_scp(distfile, location)

    def run_scp(self, distfile, location):
        if not self.process.quiet:
            print('running scp_upload')
            self.delay()
            name = basename(distfile)
            print('Uploading dist/%(name)s to %(location)s' % locals())

        try:
            rc, lines = self.process.popen(
                'scp "%(distfile)s" "%(location)s"' % locals(),
                echo=False)
            if rc == 0:
                if not self.process.quiet:
                    print('OK')
                return rc
        except KeyboardInterrupt:
            pass
        err_exit('ERROR: scp failed')

    def run_sftp(self, distfile, location):
        if not self.process.quiet:
            print('running sftp_upload')
            self.delay()
            name = basename(distfile)
            print('Uploading dist/%(name)s to %(location)s' % locals())

        with tempfile.NamedTemporaryFile() as file:
            cmds = 'put "%(distfile)s"\nbye\n' % locals()
            if sys.version_info[0] >= 3:
                cmds = encode(cmds)
            file.write(cmds)
            file.flush()
            cmdfile = file.name

            try:
                rc, lines = self.process.popen(
                    'sftp -b "%(cmdfile)s" "%(location)s"' % locals(),
                    echo=False)
                if rc == 0:
                    if not self.process.quiet:
                        print('OK')
                    return rc
            except KeyboardInterrupt:
                pass
            err_exit('ERROR: sftp failed')

