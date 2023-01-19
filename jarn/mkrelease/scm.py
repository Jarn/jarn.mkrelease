from __future__ import absolute_import

import os
import re

from operator import itemgetter
from lazy import lazy

from os.path import abspath, join, expanduser, dirname
from os.path import exists, isdir, isfile

from .process import Process
from .urlparser import URLParser
from .chdir import ChdirStack, chdir
from .tee import NotEmpty
from .exit import err_exit as _err_exit, warn


def err_exit(msg, rc=1):
    _err_exit('mkrelease: '+msg, rc)


class SCM(object):
    """Interface to source code management systems."""

    name = ''
    version_re = re.compile(r'version ([0-9.]+)', re.IGNORECASE)

    def __init__(self, process=None, urlparser=None):
        self.process = process or Process(env=self.get_env())
        self.urlparser = urlparser or URLParser()
        self.dirstack = ChdirStack()

    @lazy
    def version_info(self):
        version = self.get_version()
        info = []
        if version:
            for number in version.split('.'):
                try:
                    info.append(int(number, 10))
                except (TypeError, ValueError):
                    break
        return tuple(info)

    def get_version(self):
        raise NotImplementedError

    def get_env(self):
        env = os.environ.copy()
        if 'PYTHONPATH' in env:
            del env['PYTHONPATH']
        return env

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

    def get_root_from_sandbox(self, dir):
        raise NotImplementedError

    def get_branch_from_sandbox(self, dir):
        raise NotImplementedError

    def get_url_from_sandbox(self, dir):
        raise NotImplementedError

    def commit_sandbox(self, dir, name, version, push):
        raise NotImplementedError

    def clone_url(self, url, dir):
        raise NotImplementedError

    def make_branchid(self, dir, branch):
        raise NotImplementedError

    def switch_branch(self, dir, branch):
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


class Subversion(SCM):

    name = 'svn'

    def get_version(self):
        rc, lines = self.process.popen(
            'svn --version', echo=False)
        if rc == 0 and lines:
            match = self.version_re.search(lines[0])
            if match is not None:
                return match.group(1)
        return ''

    def is_valid_url(self, url):
        return self.urlparser.get_scheme(url) in \
            ('svn', 'svn+ssh', 'http', 'https', 'file')

    def is_valid_sandbox(self, dir):
        if isdir(dir):
            rc, lines = self.process.popen(
                'svn info "%(dir)s"' % locals(), echo=False, echo2=False)
            if rc == 0:
                return True
        return False

    def is_same_sandbox(self, dir, child_url):
        rc, lines = self.process.popen(
            'svn info "%(dir)s"' % locals(), echo=False, echo2=False)
        if rc == 0 and lines:
            if self.version_info[:2] >= (1, 7):
                url = lines[2][5:]
            else:
                url = lines[1][5:]
            if child_url.startswith(url):
                return True
        return False

    def is_dirty_sandbox(self, dir):
        rc, lines = self.process.popen(
            'svn status "%(dir)s"' % locals(), echo=False)
        if rc == 0:
            for line in lines:
                if line[0:1] in ('M', 'A', 'R', 'D'):
                    return True
                if line[1:2] in ('M',):
                    return True
            return False
        err_exit('Failed to get status from %(dir)s' % locals())

    def is_unclean_sandbox(self, dir):
        rc, lines = self.process.popen(
            'svn status "%(dir)s"' % locals(), echo=False)
        if rc == 0:
            for line in lines:
                if line[0:1] in ('M', 'A', 'R', 'D', 'C', '!', '~'):
                    return True
                if line[1:2] in ('M', 'C'):
                    return True
                if self.version_info[:2] >= (1, 6):
                    if line[6:7] in ('C',):
                        return True
            return False
        err_exit('Failed to get status from %(dir)s' % locals())

    def is_remote_sandbox(self, dir):
        return bool(self.get_url_from_sandbox(dir))

    def get_root_from_sandbox(self, dir):
        rc, lines = self.process.popen(
            'svn info "%(dir)s"' % locals(), echo=False)
        if rc == 0 and lines:
            if self.version_info[:2] >= (1, 7):
                url = lines[2][5:]
            else:
                url = lines[1][5:]
            if not self.is_same_sandbox(dirname(dir), url):
                return dir
            return self.get_root_from_sandbox(dirname(dir))
        err_exit('Failed to get root from %(dir)s' % locals())

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
            err_exit('Failed to get branch from %(url)s' % locals())
        return '/'.join(parts)

    def get_base_url_from_sandbox(self, dir):
        url = self.get_url_from_sandbox(dir)
        parts = url.split('/')
        for i in reversed(range(len(parts))):
            if parts[i] in ('trunk', 'branches', 'tags', 'branch', 'tag'):
                parts = parts[:i]
                break
        else:
            err_exit('Failed to get layout from %(url)s' % locals())
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
        err_exit('No tags directory found in %(url)s' % locals())

    def get_url_from_sandbox(self, dir):
        rc, lines = self.process.popen(
            'svn info "%(dir)s"' % locals(), echo=False)
        if rc == 0 and lines:
            if self.version_info[:2] >= (1, 7):
                return lines[2][5:]
            else:
                return lines[1][5:]
        err_exit('Failed to get URL from %(dir)s' % locals())

    def commit_sandbox(self, dir, name, version, push):
        rc, lines = self.process.popen(
            'svn commit -m"Prepare %(name)s %(version)s." "%(dir)s"' % locals())
        if rc != 0:
            err_exit('Commit failed')
        return rc

    def clone_url(self, url, dir):
        rc, lines = self.process.popen(
            'svn checkout "%(url)s" "%(dir)s"' % locals())
        if rc != 0:
            err_exit('Checkout failed')
        return rc

    def make_branchid(self, dir, branch):
        if self.urlparser.get_scheme(branch) == 'file':
            return self.urlparser.abspath(branch)
        return branch

    @chdir
    def switch_branch(self, dir, branch):
        rc, lines = self.process.popen(
            'svn switch "%(branch)s"' % locals())
        if rc != 0:
            err_exit('Switch failed')
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
        rc, lines = self.process.popen(
            ('svn copy -m"Tagged %(name)s %(version)s." "%(url)s" "%(tagid)s"' % locals()),
            echo=NotEmpty())
        if rc != 0:
            err_exit('Tag failed')
        return rc


class Mercurial(SCM):

    name = 'hg'

    def get_version(self):
        rc, lines = self.process.popen(
            'hg --version', echo=False)
        if rc == 0 and lines:
            match = self.version_re.search(lines[0])
            if match is not None:
                return match.group(1)
        return ''

    def is_valid_url(self, url):
        return self.urlparser.get_scheme(url) in \
            ('ssh', 'http', 'https', 'file')

    def is_valid_sandbox(self, dir):
        if isdir(dir):
            self.dirstack.push(dir)
            try:
                rc, lines = self.process.popen(
                    'hg status', echo=False, echo2=False)
                if rc == 0:
                    return True
            finally:
                self.dirstack.pop()
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
    def get_root_from_sandbox(self, dir):
        rc, lines = self.process.popen(
            'hg root', echo=False)
        if rc == 0 and lines:
            return lines[0]
        err_exit('Failed to get root from %(dir)s' % locals())

    @chdir
    def get_branch_from_sandbox(self, dir):
        rc, lines = self.process.popen(
            'hg branch', echo=False)
        if rc == 0 and lines:
            return lines[0]
        err_exit('Failed to get branch from %(dir)s' % locals())

    @chdir
    def get_url_from_sandbox(self, dir):
        self.get_branch_from_sandbox(dir) # Called here for its error checking only
        rc, lines = self.process.popen(
            'hg show paths.default', echo=False)
        if rc in (0, 1):    # 1 means no paths.default (3.1.1)
            if lines:
                return lines[0]
        else:
            err_exit('Failed to get URL from %(dir)s' % locals())
        return ''

    @chdir
    def commit_sandbox(self, dir, name, version, push):
        rc, lines = self.process.popen(
            'hg commit -v -m"Prepare %(name)s %(version)s." .' % locals())
        if rc not in (0, 1):    # 1 means empty commit
            err_exit('Commit failed')
        rc = 0
        if push:
            if self.is_remote_sandbox(dir):
                rc, lines = self.process.popen(
                    'hg push default')
                if rc not in (0, 1):    # 1 means empty push (2.1)
                    err_exit('Push failed')
                rc = 0
            else:
                warn('No default path found; not pushing the commit')
        return rc

    def clone_url(self, url, dir):
        rc, lines = self.process.popen(
            'hg clone "%(url)s" "%(dir)s"' % locals())
        if rc != 0:
            err_exit('Clone failed')
        return rc

    def make_branchid(self, dir, branch):
        return branch

    @chdir
    def switch_branch(self, dir, branch):
        rc, lines = self.process.popen(
            'hg update "%(branch)s"' % locals())
        if rc != 0:
            err_exit('Update failed')
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
        rc, lines = self.process.popen(
            'hg tag -m"Tagged %(name)s %(version)s." "%(tagid)s"' % locals())
        if rc != 0:
            err_exit('Tag failed')
        if push:
            if self.is_remote_sandbox(dir):
                rc, lines = self.process.popen(
                    'hg push default')
                if rc != 0:
                    err_exit('Push failed')
            else:
                warn('No default path found; not pushing the tag')
        return rc


class Git(SCM):

    name = 'git'

    def get_version(self):
        rc, lines = self.process.popen(
            'git --version', echo=False)
        if rc == 0 and lines:
            match = self.version_re.search(lines[0])
            if match is not None:
                return match.group(1)
        return ''

    def is_valid_url(self, url):
        if self.urlparser.get_scheme(url) in \
            ('git', 'ssh', 'rsync', 'http', 'https', 'file'):
            return True
        if self.urlparser.is_ssh_url(url):
            return True
        return False

    def is_valid_sandbox(self, dir):
        if isdir(dir):
            self.dirstack.push(dir)
            try:
                rc, lines = self.process.popen(
                    'git rev-parse --is-inside-work-tree', echo=False, echo2=False)
                if rc == 0 and lines:
                    return lines[0] == 'true'
            finally:
                self.dirstack.pop()
        return False

    @chdir
    def is_dirty_sandbox(self, dir):
        if self.version_info[:2] >= (1, 7):
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
    def get_root_from_sandbox(self, dir):
        rc, lines = self.process.popen(
            'git rev-parse --show-toplevel', echo=False)
        if rc == 0 and lines:
            return lines[0]
        err_exit('Failed to get root from %(dir)s' % locals())

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
            for line in reversed(lines):
                if line.startswith(key):
                    return line[len(key):]
        else:
            err_exit('Failed to get remote from %(branch)s' % locals())
        return ''

    @chdir
    def get_tracked_branch_from_sandbox(self, dir):
        branch = self.get_branch_from_sandbox(dir)
        rc, lines = self.process.popen(
            'git config -l', echo=False)
        if rc == 0 and lines:
            key = 'branch.%(branch)s.merge=' % locals()
            for line in reversed(lines):
                if line.startswith(key):
                    return line[len(key)+len('refs/heads/'):]
        else:
            err_exit('Failed to get tracked branch from %(branch)s' % locals())
        return ''

    @chdir
    def get_url_from_sandbox(self, dir):
        remote = self.get_remote_from_sandbox(dir)
        if remote:
            rc, lines = self.process.popen(
                'git config -l', echo=False)
            if rc == 0 and lines:
                key = 'remote.%(remote)s.url=' % locals()
                for line in reversed(lines):
                    if line.startswith(key):
                        return line[len(key):]
            else:
                err_exit('Failed to get URL from %(dir)s' % locals())
        return ''

    @chdir
    def commit_sandbox(self, dir, name, version, push):
        rc, lines = self.process.popen(
            'git commit -m"Prepare %(name)s %(version)s." .' % locals())
        if rc not in (0, 1):    # 1 means empty commit
            err_exit('Commit failed')
        rc = 0
        if push:
            branch = self.get_branch_from_sandbox(dir)
            remote = self.get_remote_from_sandbox(dir)
            if remote:
                tracked = self.get_tracked_branch_from_sandbox(dir)
                if tracked:
                    rc, lines = self.process.popen(
                        'git push "%(remote)s" "%(branch)s:%(tracked)s"' % locals())
                    if rc != 0:
                        err_exit('Push failed')
                    return rc
            warn('%(branch)s does not track a remote branch; '
                 'not pushing the commit' % locals())
        return rc

    def clone_url(self, url, dir):
        rc, lines = self.process.popen(
            'git clone "%(url)s" "%(dir)s"' % locals())
        if rc != 0:
            err_exit('Clone failed')
        return rc

    def make_branchid(self, dir, branch):
        return branch or 'master'

    @chdir
    def switch_branch(self, dir, branch):
        rc, lines = self.process.popen(
            'git checkout -q "%(branch)s"' % locals())
        if rc != 0:
            err_exit('Checkout failed')
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
        rc, lines = self.process.popen(
            'git tag -m"Tagged %(name)s %(version)s." "%(tagid)s"' % locals())
        if rc != 0:
            err_exit('Tag failed')
        if push:
            branch = self.get_branch_from_sandbox(dir)
            remote = self.get_remote_from_sandbox(dir)
            if remote:
                tracked = self.get_tracked_branch_from_sandbox(dir)
                if tracked:
                    rc, lines = self.process.popen(
                        'git push "%(remote)s" tag "%(tagid)s"' % locals())
                    if rc != 0:
                        err_exit('Push failed')
                    return rc
            warn('%(branch)s does not track a remote branch; '
                 'not pushing the tag' % locals())
        return rc


class SCMFactory(object):
    """Hands out SCM objects."""

    scms = (Subversion, Mercurial, Git)

    def __init__(self, urlparser=None):
        self.urlparser = urlparser or URLParser()

    def get_scm_from_type(self, type):
        for klass in self.scms:
            if klass.name == type:
                return klass()
        err_exit('Unsupported SCM type: %(type)s' % locals())

    def get_scm_from_sandbox(self, dir):
        dir = abspath(expanduser(dir))
        if not exists(dir):
            err_exit('No such file or directory: %(dir)s' % locals())
        matches = self._find_scms(dir)
        if not matches:
            err_exit('Not a sandbox: %(dir)s' % locals())
        if len(matches) == 1:
            return matches[0]
        matches = self._find_closest(dir, matches)
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

    def _find_scms(self, dir):
        # Find all SCMs in dir
        matches = []
        for klass in self.scms:
            if klass().is_valid_sandbox(dir):
                matches.append(klass())
        return matches

    def _find_closest(self, dir, matches):
        # Find SCMs with closest root
        roots = []
        for scm in matches:
            root = scm.get_root_from_sandbox(dir)
            roots.append((len(root), scm))
        sorted_roots = sorted(roots, key=itemgetter(0))
        longest = sorted_roots[-1][0]
        return [x[1] for x in roots if x[0] == longest]

    def get_scm_from_url(self, url):
        scheme, user, host, path, qs, frag = self.urlparser.urlsplit(url)
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
            if user == 'git' or host == 'github.com':
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
            if user == 'git' or host == 'github.com':
                return Git()
            err_exit('Failed to guess SCM type: %(url)s\n'
                     'Please specify --svn, --hg, or --git' % locals())
        if scheme in ('file',):
            if path.endswith('.git'):
                return Git()
            if host in ('', 'localhost'):
                # Strip leading slash to allow tilde expansion
                if host and path.startswith('/~'):
                    path = path[1:]
                if self._is_bare_git_repo(path):
                    return Git()
                if self._is_subversion_repo(path):
                    return Subversion()
                return self._get_scm_from_file_url(path)
            err_exit('Failed to guess SCM type: %(url)s\n'
                     'Please specify --svn, --hg, or --git' % locals())
        err_exit('Unsupported URL scheme: %(scheme)s' % locals())

    def _is_bare_git_repo(self, dir):
        # Detect bare Git repo
        def is_repo(dir):
            return (isfile(join(dir, 'config')) and
                    isdir(join(dir, 'refs', 'heads')) and
                    isdir(join(dir, 'refs', 'tags')))
        dir = abspath(expanduser(dir))
        return is_repo(dir)

    def _is_subversion_repo(self, dir):
        # Detect Subversion repo
        def is_repo(dir):
            return (isfile(join(dir, 'format')) and
                    isdir(join(dir, 'db', 'revs')) and
                    isdir(join(dir, 'db', 'revprops')))
        dir = abspath(expanduser(dir))
        parts = dir.split('/')
        for i in range(len(parts)):
            dir = '/'.join(parts[:i+1]) or '/'
            if is_repo(dir):
                return True
        return False

    def _get_scm_from_file_url(self, dir):
        # Return clonable repository roots only
        dir = abspath(expanduser(dir))
        if not exists(dir):
            err_exit('No such file or directory: %(dir)s' % locals())
        matches = self._find_scms(dir)
        matches = self._find_clonable(dir, matches)
        if not matches:
            err_exit('Not a repository: %(dir)s' % locals())
        matches = self._find_roots(dir, matches)
        if not matches:
            err_exit('Not a repository root: %(dir)s' % locals())
        if len(matches) == 1:
            return matches[0]
        if len(matches) == 2:
            names = '%s and %s' % tuple([x.__class__.__name__ for x in matches])
            flags = '--%s or --%s' % tuple([x.name for x in matches])
        err_exit('%(names)s found in %(dir)s\n'
                 'Please specify %(flags)s to resolve' % locals())

    def _find_clonable(self, dir, matches):
        return [x for x in matches if x.name != 'svn']

    def _find_roots(self, dir, matches):
        return [x for x in matches if x.get_root_from_sandbox(dir) == dir]

    def get_scm(self, type, url_or_dir):
        if type:
            scm = self.get_scm_from_type(type)
        elif self.urlparser.is_url(url_or_dir):
            scm = self.get_scm_from_url(url_or_dir)
        elif self.urlparser.is_ssh_url(url_or_dir):
            scm = Git()
        else:
            scm = self.get_scm_from_sandbox(url_or_dir)
        return scm

