import re

from urlparse import urlsplit
from os.path import abspath


class URLParser(object):
    """A minimal URL parser and splitter."""

    scheme_re = re.compile(r'^(\S+?)://|^(file):')

    def get_scheme(self, url):
        match = self.scheme_re.match(url)
        if match is not None:
            return match.group(1) or match.group(2) or ''
        return ''

    def is_url(self, url):
        return bool(self.get_scheme(url))

    def split(self, url):
        scheme = self.get_scheme(url)
        if scheme:
            # Split all URLs like HTTP URLs
            url = 'http%s' % url[len(scheme):]
            ignored, host, path, qs, frag = urlsplit(url)
            if scheme == 'file' and not host:
                path = abspath(path)
            user, host = self._hostsplit(host)
            return scheme, user, host, path, qs, frag
        return '', '', '', url, '', ''

    def _hostsplit(self, host):
        if '@' in host:
            return host.split('@', 1)
        return '', host

