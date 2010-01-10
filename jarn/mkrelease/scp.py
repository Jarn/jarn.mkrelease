from process import Process
from exit import err_exit


class SCP(object):
    """Secure copy abstraction."""

    def __init__(self, process=None):
        self.process = process or Process()

    def has_host(self, location):
        colon = location.find(':')
        slash = location.find('/')
        return colon > 0 and (slash < 0 or slash > colon)

    def join(distbase, location):
        sep = ''
        if distbase and distbase[-1] not in (':', '/'):
            sep = '/'
        return distbase + sep + location

    def run_scp(self, distfile, location):
        rc = self.process.os_system(
            'scp "%(distfile)s" "%(location)s"' % locals())
        if rc != 0:
            err_exit('Scp failed')
        return rc

