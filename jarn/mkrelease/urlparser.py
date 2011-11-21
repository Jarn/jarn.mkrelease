import re

from os.path import abspath, expanduser
from urlparse import urlsplit, urlunsplit

from scp import SCP


class URLParser(object):
    """A minimal URL parser and splitter."""

    scheme_re = re.compile(r'^(\S+?)://|^(file):')
    git_ssh_re = re.compile(r'^(\S+?):(.*)')

    def __init__(self):
        self.scp = SCP()

    def get_scheme(self, url):
        match = self.scheme_re.match(url)
        if match is not None:
            return match.group(1) or match.group(2)
        return ''

    def is_url(self, url):
        return bool(self.get_scheme(url))

    def is_git_ssh_url(self, url):
        return (not self.is_url(url) and
                self.git_ssh_re.match(url) is not None and
                self.scp.has_host(url))

    def split(self, url):
        scheme = self.get_scheme(url)
        if scheme:
            ignored, host, path, qs, frag = urlsplit(url)
            user, host = self.hostsplit(host)
            return scheme, user, host, path, qs, frag
        return '', '', '', url, '', ''

    def hostsplit(self, host):
        if '@' in host:
            return host.split('@', 1)
        return '', host

    def hostunsplit(self, user, host):
        if user:
            return '%s@%s' % (user, host)
        return host

    def abspath(self, url):
        scheme = self.get_scheme(url)
        if scheme == 'file':
            ignored, user, host, path, qs, frag = self.split(url)
            if host in ('', 'localhost'):
                # Strip leading slash to allow tilde expansion
                if host and path.startswith('/~'):
                    path = path[1:]
                path = abspath(expanduser(path))
                host = self.hostunsplit(user, host)
                return urlunsplit((scheme, host, path, qs, frag))
        return url

