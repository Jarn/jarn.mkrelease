import re

from os.path import abspath, expanduser
from urlparse import urlsplit, urlunsplit


class URLParser(object):
    """A minimal URL parser and splitter."""

    scheme_re = re.compile(r'^(\S+?)://|^(file):')

    def get_scheme(self, url):
        match = self.scheme_re.match(url)
        if match is not None:
            return match.group(1) or match.group(2)
        return ''

    def is_url(self, url):
        return bool(self.get_scheme(url))

    def split(self, url):
        scheme = self.get_scheme(url)
        if scheme:
            ignored, host, path, qs, frag = urlsplit(url)
            user, host = self._hostsplit(host)
            return scheme, user, host, path, qs, frag
        return '', '', '', url, '', ''

    def abspath(self, url):
        scheme = self.get_scheme(url)
        if scheme == 'file':
            ignored, user, host, path, qs, frag = self.split(url)
            if host in ('', 'localhost'):
                # Strip leading slash to allow tilde expansion
                if host and path.startswith('/~'):
                    path = path[1:]
                path = abspath(expanduser(path))
                host = self._hostunsplit(user, host)
                return urlunsplit((scheme, host, path, qs, frag))
        return url

    def _hostsplit(self, host):
        if '@' in host:
            return host.split('@', 1)
        return '', host

    def _hostunsplit(self, user, host):
        if user:
            return '%s@%s' % (user, host)
        return host

