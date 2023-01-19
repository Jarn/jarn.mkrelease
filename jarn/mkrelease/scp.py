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
from .colors import bold


class SCP(object):
    """Secure copy and FTP abstraction."""

    def __init__(self, process=None, defaults=None):
        self.process = process or Process()

        if defaults and not defaults.interactive:
            self.interactive = False
        else:
            self.interactive = True

    def get_options(self):
        if not self.interactive:
            return '-o KbdInteractiveAuthentication=no'
        else:
            return ''

    def run_upload(self, scheme, distfiles, location):
        distfiles = sorted(distfiles, key=len, reverse=True)
        if scheme == 'sftp':
            if not self.process.quiet:
                print(bold('running sftp_upload'))
                print('Uploading distributions to %(location)s' % locals())
            for distfile in distfiles:
                self.run_sftp(distfile, location)
        else:
            if not self.process.quiet:
                print(bold('running scp_upload'))
                print('Uploading distributions to %(location)s' % locals())
            for distfile in distfiles:
                self.run_scp(distfile, location)
        return 0

    def run_scp(self, distfile, location):
        if not self.process.quiet:
            name = basename(distfile)
            print('Uploading %(name)s' % locals())

        options = self.get_options()
        rc, lines = self.process.popen(
            'scp %(options)s "%(distfile)s" "%(location)s"' % locals(),
            echo=False)
        if rc == 0:
            return rc
        err_exit('ERROR: upload failed')

    def run_sftp(self, distfile, location):
        if not self.process.quiet:
            name = basename(distfile)
            print('Uploading %(name)s' % locals())

        with tempfile.NamedTemporaryFile() as file:
            cmds = 'put "%(distfile)s"\nbye\n' % locals()
            if sys.version_info[0] >= 3:
                cmds = encode(cmds)
            file.write(cmds)
            file.flush()
            cmdfile = file.name

            options = self.get_options()
            rc, lines = self.process.popen(
                'sftp %(options)s -b "%(cmdfile)s" "%(location)s"' % locals(),
                echo=False)
            if rc == 0:
                return rc
            err_exit('ERROR: upload failed')

