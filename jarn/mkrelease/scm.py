from os.path import abspath, join, expanduser, exists, isdir

from process import Process
from urlparser import URLParser
from dirstack import DirStack, chdir
from exit import err_exit, warn
from lazy import lazy

import re
version_re = re.compile(r'version ([0-9.]+)', re.IGNORECASE)


class SCM(object):
    """Interface to source code management systems."""

    name = ''

    def __init__(self, process=None):
        self.process = process or Process()

    def get_version(self):
        raise NotImplementedError

    def is_valid_url(self, url):
        raise NotImplementedError

    def is_valid_sandbox(self, dir):
        raise NotImplementedError

    def is_dirty_sandbox(self, dir):
        raise NotImplementedError

    def is_unclean_sandbox(self, dir):
        raise NotImplementedError

    def is_remote_sandbox(self, dir):
        raise NotImplementedError

    def get_branch_from_sandbox(self, dir):
        raise NotImplementedError

    def get_url_from_sandbox(self, dir):
        raise NotImplementedError

    def checkin_sandbox(self, dir, name, version, push):
        raise NotImplementedError

    def checkout_url(self, url, dir):
        raise NotImplementedError

    def make_tagid(self, dir, version):
        raise NotImplementedError

    def tag_exists(self, dir, tagid):
        raise NotImplementedError

    def create_tag(self, dir, tagid, name, version, push):
        raise NotImplementedError

    def check_valid_sandbox(self, dir):
        if not exists(dir):
            err_exit('No such file or directory: %(dir)s' % locals())
        if not self.is_valid_sandbox(dir):
            name = self.__class__.__name__
            err_exit('Not a %(name)s sandbox: %(dir)s' % locals())

    def check_dirty_sandbox(self, dir):
        if self.is_dirty_sandbox(dir):
            err_exit('Uncommitted changes in %(dir)s' % locals())

    def check_unclean_sandbox(self, dir):
        if self.is_unclean_sandbox(dir):
            err_exit('Unclean sandbox: %(dir)s' % locals())

    def check_tag_exists(self, dir, tagid):
        if self.tag_exists(dir, tagid):
            err_exit('Tag exists: %(tagid)s' % locals())

    @lazy
    def version_tuple(self):
        version = self.get_version()
        r = []
        if version:
            for number in version.split('.'):
                try:
                    r.append(int(number))
                except (TypeError, ValueError):
                    break
        return tuple(r)


class Subversion(SCM):

    name = 'svn'

    def get_version(self):
        rc, lines = self.process.popen(
            'svn --version', echo=False)
        if rc == 0 and lines:
            match = version_re.search(lines[0])
            if match is not None:
                return match.group(1)
        return None

    def is_valid_url(self, url):
        return url.startswith(
            ('svn://', 'svn+ssh://', 'http://', 'https://', 'file://'))

    def is_valid_sandbox(self, dir):
        if isdir(join(dir, '.svn')):
            rc, lines = self.process.popen(
                'svn info "%(dir)s"' % locals(), echo=False, echo2=False)
            if rc == 0:
                return True
        return False

    def is_dirty_sandbox(self, dir):
        rc, lines = self.process.popen(
            'svn status "%(dir)s"' % locals(), echo=False)
        if rc == 0:
            lines = [x for x in lines if x[0:1] in ('M', 'A', 'R', 'D')]
            return bool(lines)
        err_exit('Failed to get status from %(dir)s' % locals())

    def is_unclean_sandbox(self, dir):
        rc, lines = self.process.popen(
            'svn status "%(dir)s"' % locals(), echo=False)
        if rc == 0:
            lines = [x for x in lines if x[0:1] in ('M', 'A', 'R', 'D', 'C', '!', '~')]
            return bool(lines)
        err_exit('Failed to get status from %(dir)s' % locals())

    def is_remote_sandbox(self, dir):
        return bool(self.get_url_from_sandbox(dir))

    def get_branch_from_sandbox(self, dir):
        url = self.get_url_from_sandbox(dir)
        parts = url.split('/')
        for i in reversed(range(len(parts))):
            if parts[i] == 'trunk':
                parts = parts[:i+1]
                break
            elif parts[i] in ('branches', 'tags', 'branch', 'tag'):
                parts = parts[:i+2]
                break
        else:
            err_exit('Failed to get branch from %(dir)s' % locals())
        return '/'.join(parts)

    def get_base_url_from_sandbox(self, dir):
        url = self.get_url_from_sandbox(dir)
        parts = url.split('/')
        for i in reversed(range(len(parts))):
            if parts[i] in ('trunk', 'branches', 'tags', 'branch', 'tag'):
                parts = parts[:i]
                break
        else:
            err_exit('Failed to get layout from %(dir)s' % locals())
        return '/'.join(parts)

    def get_layout_from_sandbox(self, dir):
        url = self.get_base_url_from_sandbox(dir)
        rc, lines = self.process.popen(
            'svn list "%(url)s"' % locals(), echo=False)
        if rc == 0:
            for line in lines:
                if line[:-1] == 'tag':
                    return ('trunk', 'branch', 'tag')
                if line[:-1] == 'tags':
                    return ('trunk', 'branches', 'tags')
        err_exit('Failed to get layout from %(dir)s' % locals())

    def get_url_from_sandbox(self, dir):
        rc, lines = self.process.popen(
            'svn info "%(dir)s"' % locals(), echo=False)
        if rc == 0 and lines:
            return lines[1][5:]
        err_exit('Failed to get URL from %(dir)s' % locals())

    def checkin_sandbox(self, dir, name, version, push):
        rc = self.process.system(
            'svn commit -m"Prepare %(name)s %(version)s." "%(dir)s"' % locals())
        if rc != 0:
            err_exit('Commit failed')
        return rc

    def checkout_url(self, url, dir):
        rc = self.process.system(
            'svn checkout "%(url)s" "%(dir)s"' % locals())
        if rc != 0:
            err_exit('Checkout failed')
        return rc

    def make_tagid(self, dir, version):
        url = self.get_url_from_sandbox(dir)
        parts = url.split('/')
        if parts[-1] == 'trunk':
            parts = parts[:-1]
        elif parts[-2] in ('branches', 'tags', 'branch', 'tag'):
            parts = parts[:-2]
        else:
            err_exit('URL must point to trunk, branch, or tag: %(url)s' % locals())
        layout = self.get_layout_from_sandbox(dir)
        return '/'.join(parts + [layout[2], version])

    def tag_exists(self, dir, tagid):
        url, version = tagid.rsplit('/', 1)
        rc, lines = self.process.popen(
            'svn list "%(url)s"' % locals(), echo=False)
        if rc == 0:
            for line in lines:
                if line[:-1] == version:
                    return True
            return False
        err_exit('Failed to get tags from %(url)s' % locals())

    def create_tag(self, dir, tagid, name, version, push):
        url = self.get_url_from_sandbox(dir)
        rc = self.process.system(
            'svn copy -m"Tagged %(name)s %(version)s." "%(url)s" "%(tagid)s"' % locals())
        if rc != 0:
            err_exit('Tag failed')
        return rc


class Mercurial(SCM):

    name = 'hg'

    def get_version(self):
        rc, lines = self.process.popen(
            'hg --version', echo=False)
        if rc == 0 and lines:
            match = version_re.search(lines[0])
            if match is not None:
                return match.group(1)
        return None

    def is_valid_url(self, url):
        return url.startswith(
            ('ssh://', 'http://', 'https://', 'file://'))

    def is_valid_sandbox(self, dir):
        if isdir(dir):
            dirstack = DirStack()
            dirstack.push(dir)
            try:
                rc, lines = self.process.popen(
                    'hg status', echo=False, echo2=False)
                if rc == 0:
                    return True
            finally:
                dirstack.pop()
        return False

    @chdir
    def is_dirty_sandbox(self, dir):
        rc, lines = self.process.popen(
            'hg status -mar .', echo=False)
        if rc == 0:
            return bool(lines)
        err_exit('Failed to get status from %(dir)s' % locals())

    @chdir
    def is_unclean_sandbox(self, dir):
        rc, lines = self.process.popen(
            'hg status -mard .', echo=False)
        if rc == 0:
            return bool(lines)
        err_exit('Failed to get status from %(dir)s' % locals())

    @chdir
    def is_remote_sandbox(self, dir):
        return bool(self.get_url_from_sandbox(dir))

    @chdir
    def get_branch_from_sandbox(self, dir):
        rc, lines = self.process.popen(
            'hg branch', echo=False)
        if rc == 0 and lines:
            return lines[0]
        err_exit('Failed to get branch from %(dir)s' % locals())

    @chdir
    def get_url_from_sandbox(self, dir):
        self.get_branch_from_sandbox(dir) # Called here for its error checking
        rc, lines = self.process.popen(
            'hg show paths.default', echo=False)
        if rc == 0:
            if lines:
                return lines[0]
        else:
            err_exit('Failed to get URL from %(dir)s' % locals())
        return ''

    @chdir
    def checkin_sandbox(self, dir, name, version, push):
        rc = self.process.system(
            'hg commit -v -m"Prepare %(name)s %(version)s." .' % locals())
        if rc != 0:
            err_exit('Commit failed')
        if push and self.is_remote_sandbox(dir):
            rc = self.process.system(
                'hg push')
            if rc != 0:
                err_exit('Push failed')
        return rc

    def checkout_url(self, url, dir):
        rc = self.process.system(
            'hg clone -v "%(url)s" "%(dir)s"' % locals())
        if rc != 0:
            err_exit('Clone failed')
        return rc

    def make_tagid(self, dir, version):
        return version

    @chdir
    def tag_exists(self, dir, tagid):
        rc, lines = self.process.popen(
            'hg tags', echo=False)
        if rc == 0:
            for line in lines:
                if line.split()[0] == tagid:
                    return True
            return False
        err_exit('Failed to get tags from %(dir)s' % locals())

    @chdir
    def create_tag(self, dir, tagid, name, version, push):
        rc = self.process.system(
            'hg tag -m"Tagged %(name)s %(version)s." "%(tagid)s"' % locals())
        if rc != 0:
            err_exit('Tag failed')
        if push and self.is_remote_sandbox(dir):
            rc = self.process.system(
                'hg push')
            if rc != 0:
                err_exit('Push failed')
        return rc


class Git(SCM):

    name = 'git'

    def get_version(self):
        rc, lines = self.process.popen(
            'git --version', echo=False)
        if rc == 0 and lines:
            match = version_re.search(lines[0])
            if match is not None:
                return match.group(1)
        return None

    def is_valid_url(self, url):
        return url.startswith(
            ('git://', 'ssh://', 'rsync://', 'http://', 'https://', 'file://'))

    def is_valid_sandbox(self, dir):
        if isdir(dir):
            dirstack = DirStack()
            dirstack.push(dir)
            try:
                rc, lines = self.process.popen(
                    'git branch', echo=False, echo2=False)
                if rc == 0:
                    return True
            finally:
                dirstack.pop()
        return False

    @chdir
    def is_dirty_sandbox(self, dir):
        if self.version_tuple[:2] >= (1, 7):
            rc, lines = self.process.popen(
                'git status --porcelain --untracked-files=no .', echo=False)
            if rc == 0:
                return bool(lines)
        else:
            rc, lines = self.process.popen(
                'git status .', echo=False)
            if rc == 0:
                return True
            if rc == 1:
                return False
        err_exit('Failed to get status from %(dir)s' % locals())

    @chdir
    def is_unclean_sandbox(self, dir):
        return self.is_dirty_sandbox(dir)

    @chdir
    def is_remote_sandbox(self, dir):
        return bool(self.get_remote_from_sandbox(dir))

    @chdir
    def get_branch_from_sandbox(self, dir):
        rc, lines = self.process.popen(
            'git branch', echo=False)
        if rc == 0:
            for line in lines:
                if line.startswith('*'):
                    return line[2:]
        err_exit('Failed to get branch from %(dir)s' % locals())

    @chdir
    def get_remote_from_sandbox(self, dir):
        branch = self.get_branch_from_sandbox(dir)
        rc, lines = self.process.popen(
            'git config -l', echo=False)
        if rc == 0 and lines:
            key = 'branch.%(branch)s.remote=' % locals()
            for line in lines:
                if line.startswith(key):
                    return line[len(key):]
        else:
            err_exit('Failed to get remote from %(dir)s' % locals())
        return ''

    @chdir
    def get_tracked_branch_from_sandbox(self, dir):
        branch = self.get_branch_from_sandbox(dir)
        rc, lines = self.process.popen(
            'git config -l', echo=False)
        if rc == 0 and lines:
            key = 'branch.%(branch)s.merge=' % locals()
            for line in lines:
                if line.startswith(key):
                    return line[len(key):][len('refs/heads/'):]
        else:
            err_exit('Failed to get tracked branch from %(dir)s' % locals())
        return ''

    @chdir
    def get_url_from_sandbox(self, dir):
        remote = self.get_remote_from_sandbox(dir)
        if remote:
            rc, lines = self.process.popen(
                'git config -l', echo=False)
            if rc == 0 and lines:
                key = 'remote.%(remote)s.url=' % locals()
                for line in lines:
                    if line.startswith(key):
                        return line[len(key):]
            else:
                err_exit('Failed to get URL from %(dir)s' % locals())
        return ''

    @chdir
    def checkin_sandbox(self, dir, name, version, push):
        rc = self.process.system(
            'git commit -m"Prepare %(name)s %(version)s." .' % locals())
        if rc not in (0, 1):
            err_exit('Commit failed')
        rc = 0
        remote = self.get_remote_from_sandbox(dir)
        if push and remote:
            branch = self.get_branch_from_sandbox(dir)
            tracked = self.get_tracked_branch_from_sandbox(dir)
            if tracked:
                rc = self.process.system(
                    'git push "%(remote)s" "%(branch)s:%(tracked)s"' % locals())
                if rc != 0:
                    err_exit('Push failed')
            else:
                warn('%(branch)s does not track any branch - '
                    'not pushing the commit' % locals())
        return rc

    def checkout_url(self, url, dir):
        rc = self.process.system(
            'git clone "%(url)s" "%(dir)s"' % locals())
        if rc != 0:
            err_exit('Clone failed')
        return rc

    def make_tagid(self, dir, version):
        return version

    @chdir
    def tag_exists(self, dir, tagid):
        rc, lines = self.process.popen(
            'git tag', echo=False)
        if rc == 0:
            for line in lines:
                if line == tagid:
                    return True
            return False
        err_exit('Failed to get tags from %(dir)s' % locals())

    @chdir
    def create_tag(self, dir, tagid, name, version, push):
        rc = self.process.system(
            'git tag -m"Tagged %(name)s %(version)s." "%(tagid)s"' % locals())
        if rc != 0:
            err_exit('Tag failed')
        remote = self.get_remote_from_sandbox(dir)
        if push and remote:
            branch = self.get_branch_from_sandbox(dir)
            tracked = self.get_tracked_branch_from_sandbox(dir)
            if tracked:
                rc = self.process.system(
                    'git push "%(remote)s" tag "%(tagid)s"' % locals())
                if rc != 0:
                    err_exit('Push failed')
            else:
                warn('%(branch)s does not track any branch - '
                    'not pushing the tag' % locals())
        return rc


class SCMFactory(object):
    """Hands out SCM objects."""

    scms = (Subversion, Mercurial, Git)

    def __init__(self, urlparser=None):
        self.urlparser = urlparser or URLParser()

    def get_scm_from_type(self, type):
        for scm in self.scms:
            if scm.name == type:
                return scm()
        err_exit('Unsupported SCM type: %(type)s' % locals())

    def get_scm_from_sandbox(self, dir):
        matches = []
        for scm in self.scms:
            if scm().is_valid_sandbox(dir):
                matches.append(scm())
        if not matches:
            err_exit('Not a sandbox: %(dir)s' % locals())
        if len(matches) == 1:
            return matches[0]
        if len(matches) == 2:
            names = '%s and %s' % tuple([x.__class__.__name__ for x in matches])
            flags = '--%s or --%s' % tuple([x.name for x in matches])
        elif len(matches) == 3:
            names = '%s, %s, and %s' % tuple([x.__class__.__name__ for x in matches])
            flags = '--%s, --%s, or --%s' % tuple([x.name for x in matches])
        err_exit('%(names)s found in %(dir)s\n'
                 'Please specify %(flags)s to resolve' % locals())

    def get_scm_from_url(self, url):
        scheme, user, host, path, qs, frag = self.urlparser.split(url)
        if scheme in ('svn', 'svn+ssh'):
            return Subversion()
        if scheme in ('git', 'rsync'):
            return Git()
        if scheme in ('ssh',):
            if path.endswith('.git'):
                return Git()
            if host.startswith('hg.') or path.startswith(('/hg/', '//hg/')):
                return Mercurial()
            if host.startswith('git.') or path.startswith('/git/'):
                return Git()
            err_exit('Failed to guess SCM type: %(url)s\n'
                     'Please specify --svn, --hg, or --git' % locals())
        if scheme in ('http', 'https'):
            if path.endswith('.git'):
                return Git()
            if host.startswith('svn.') or path.startswith('/svn/'):
                return Subversion()
            if host.startswith('hg.') or path.startswith('/hg/'):
                return Mercurial()
            if host.startswith('git.') or path.startswith('/git/'):
                return Git()
            err_exit('Failed to guess SCM type: %(url)s\n'
                     'Please specify --svn, --hg, or --git' % locals())
        if scheme in ('file',):
            if path.endswith('.git'):
                return Git()
            err_exit('Failed to guess SCM type: %(url)s\n'
                     'Please specify --svn, --hg, or --git' % locals())
        err_exit('Unsupported URL scheme: %(scheme)s' % locals())

    def get_scm(self, url_or_dir, type):
        if type:
            scm = self.get_scm_from_type(type)
        elif self.urlparser.is_url(url_or_dir):
            scm = self.get_scm_from_url(url_or_dir)
        else:
            dir = abspath(expanduser(url_or_dir))
            if not exists(dir):
                err_exit('No such file or directory: %(dir)s' % locals())
            scm = self.get_scm_from_sandbox(dir)
        return scm

