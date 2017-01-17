import sys
import re

from os.path import abspath, expanduser

if sys.version_info[0] >= 3:
    from urllib.parse import urlsplit, urlunsplit
else:
    from urlparse import urlsplit, urlunsplit


class URLParser(object):
    """A minimal URL parser and splitter."""

    scheme_re = re.compile(r'^(\S+?)://|^(file):')
    ssh_re = re.compile(r'^([^\s/]+?):(.*)')

    def get_scheme(self, url):
        match = self.scheme_re.match(url)
        if match is not None:
            return match.group(1) or match.group(2)
        return ''

    def is_url(self, url):
        return bool(self.get_scheme(url))

    def urlsplit(self, url):
        scheme = self.get_scheme(url)
        if scheme:
            ignored, host, path, qs, frag = urlsplit(url)
            user, host = self.hostsplit(host)
            return scheme, user, host, path, qs, frag
        return '', '', '', url, '', ''

    def urlunsplit(self, scheme, user, host, path, qs, frag):
        host = self.hostunsplit(user, host)
        return urlunsplit((scheme, host, path, qs, frag))

    def hostsplit(self, host):
        if '@' in host:
            return host.split('@', 1)
        return '', host

    def hostunsplit(self, user, host):
        if user:
            return '%s@%s' % (user, host)
        return host

    def usersplit(self, user):
        if ':' in user:
            return user.split(':', 1)
        return user, ''

    def userunsplit(self, user, password):
        if password:
            return '%s:%s' % (user, password)
        return user

    def abspath(self, url):
        scheme = self.get_scheme(url)
        if scheme == 'file':
            ignored, user, host, path, qs, frag = self.urlsplit(url)
            if host in ('', 'localhost'):
                # Strip leading slash to allow tilde expansion
                if host and path.startswith('/~'):
                    path = path[1:]
                path = abspath(expanduser(path))
                return self.urlunsplit(scheme, user, host, path, qs, frag)
        return url

    def is_ssh_url(self, url):
        return not self.is_url(url) and self.ssh_re.match(url) is not None

    def to_ssh_url(self, url):
        scheme = self.get_scheme(url)
        if scheme in ('scp', 'sftp', 'ssh'):
            ignored, user, host, path, qs, frag = self.urlsplit(url)
            user, password = self.usersplit(user)
            return scheme, self.hostunsplit(user, host) + ':' + path
        return scheme, url

