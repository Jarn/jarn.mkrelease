import os
import unittest

from jarn.mkrelease.urlparser import URLParser


class ValidUrlTests(unittest.TestCase):

    def testSvnUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('svn://'), True)

    def testSvnSshUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('svn+ssh://'), True)

    def testGitUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('git://'), True)

    def testRsyncUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('rsync://'), True)

    def testSshUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('ssh://'), True)

    def testHttpUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('http://'), True)

    def testHttpsUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('https://'), True)

    def testFileUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('file://'), True)

    def testRelativeFileUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('file:'), True)

    def testBadScheme(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('ftp//'), False)

    def testEmptyString(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url(''), False)


class UrlSplitTests(unittest.TestCase):

    def testSplitSvn(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('svn://jarn.com/public'),
                         ('svn', '', 'jarn.com', '/public', '', ''))

    def testSplitSvnSsh(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('svn+ssh://stefan@jarn.com/public'),
                         ('svn+ssh', 'stefan', 'jarn.com', '/public', '', ''))

    def testSplitGit(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('git://jarn.com/public'),
                         ('git', '', 'jarn.com', '/public', '', ''))

    def testSplitRsync(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('rsync://jarn.com/public'),
                         ('rsync', '', 'jarn.com', '/public', '', ''))

    def testSplitSsh(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('ssh://stefan@jarn.com//hg/public'),
                         ('ssh', 'stefan', 'jarn.com', '//hg/public', '', ''))

    def testSplitHttp(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('http://jarn.com/public'),
                         ('http', '', 'jarn.com', '/public', '', ''))

    def testSplitHttps(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('https://stefan:secret@jarn.com/public'),
                         ('https', 'stefan:secret', 'jarn.com', '/public', '', ''))

    def testSplitFile(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('file:///var/dist/public'),
                         ('file', '', '', '/var/dist/public', '', ''))

    def testSplitRelativeFile(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('file:var/dist/public'),
                         ('file', '', '', 'var/dist/public', '', ''))

    def testSplitRelativeFileWithTilde(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('file:~stefan/public'),
                         ('file', '', '', '~stefan/public', '', ''))

    def testSplitLocalhostWithTilde(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('file://localhost/~stefan/public'),
                         ('file', '', 'localhost', '/~stefan/public', '', ''))

    def testSplitGitWithTilde(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('git://jarn.com/~stefan/public'),
                         ('git', '', 'jarn.com', '/~stefan/public', '', ''))

    def testSplitUnsupported(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('ftp://jarn.com/public'),
                         ('ftp', '', 'jarn.com', '/public', '', ''))

    def testSplitBadUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('ssh:stefan@jarn.com/public'),
                         ('', '', '', 'ssh:stefan@jarn.com/public', '', ''))

    def testSplitScp(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('scp://stefan@jarn.com/var/dist/public'),
                         ('scp', 'stefan', 'jarn.com', '/var/dist/public', '', ''))

    def testSplitSftp(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.urlsplit('sftp://stefan@jarn.com/var/dist/public'),
                         ('sftp', 'stefan', 'jarn.com', '/var/dist/public', '', ''))


class IsUrlTests(unittest.TestCase):

    def testSvn(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('svn://jarn.com/public'), True)

    def testSvnSsh(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('svn+ssh://stefan@jarn.com/public'), True)

    def testGit(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('git://jarn.com/public'), True)

    def testRsync(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('rsync://jarn.com/public'), True)

    def testSsh(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('ssh://stefan@jarn.com//hg/public'), True)

    def testHttp(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('http://jarn.com/public'), True)

    def testHttps(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('https://jarn.com/public'), True)

    def testFile(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('file:///var/dist/public'), True)

    def testRelativeFile(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('file:var/dist/public'), True)

    def testRelativeFileWithTilde(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('file:~stefan/public'), True)

    def testLocalhostWithTilde(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('file://localhost/~stefan/public'), True)

    def testGitWithTilde(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('git://jarn.com/~stefan/public'), True)

    def testUnsupported(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('ftp://jarn.com/public'), True)

    def testUnknown(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('foo://jarn.com/public'), True)

    def testBadUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('ssh:'), False)

    def testWhitespace(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url(' http://'), False)

    def testGitSshUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_url('git@github.com:Jarn/jarn.mkrelease'), False)


class IsSshUrlTests(unittest.TestCase):

    def testGitSsh(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url('git@github.com:Jarn/jarn.mkrelease'), True)

    def testSsh(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url('ssh://'), False)

    def testGit(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url('git://'), False)

    def testUnsupported(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url('ftp://'), False)

    def testUnknown(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url('foo://'), False)

    def testFalsePositives(self):
        # Everything with a colon matches the regex...
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url('foo:'), True)

    def testColonAndPathOnly(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url(':foo'), False)

    def testSlashBeforeColon(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url('/foo:'), False)

    def testSlashColonOnly(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url('/:'), False)

    def testColonOnly(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url(':'), False)

    def testNonAlphanumeric(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url('$&%:'), True)

    def testNonConsecutive(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url('f o:'), False)

    def testBadUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url('ssh'), False)

    def testWhitespace(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url(' git@github.com:Jarn/jarn.mkrelease'), False)

    def testUserOnly(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url('stefan@:/var/dist/public'), True)

    def testEmptyString(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.is_ssh_url(''), False)


class ToSshUrlTests(unittest.TestCase):

    def testSsh(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.to_ssh_url('ssh://stefan@jarn.com/var/dist/public'),
                         ('ssh', 'stefan@jarn.com:/var/dist/public'))

    def testScp(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.to_ssh_url('scp://stefan@jarn.com/var/dist/public'),
                         ('scp', 'stefan@jarn.com:/var/dist/public'))

    def testSftp(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.to_ssh_url('sftp://stefan@jarn.com/var/dist/public'),
                         ('sftp', 'stefan@jarn.com:/var/dist/public'))

    def testIdempotence(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.to_ssh_url('stefan@jarn.com:var/dist/public'),
                         ('', 'stefan@jarn.com:var/dist/public'))
        self.assertEqual(urlparser.to_ssh_url('stefan@jarn.com:/var/dist/public'),
                         ('', 'stefan@jarn.com:/var/dist/public'))

    def testBadUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.to_ssh_url('https://stefan@jarn.com/var/dist/public'),
                         ('https', 'https://stefan@jarn.com/var/dist/public'))

    def testNoUrl(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.to_ssh_url('scp://'),
                         ('scp', ':'))

    def testNoHost(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.to_ssh_url('scp:///var/dist/public'),
                         ('scp', ':/var/dist/public'))

    def testNoPath(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.to_ssh_url('scp://stefan@jarn.com'),
                         ('scp', 'stefan@jarn.com:'))

    def testNoUser(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.to_ssh_url('scp://jarn.com/var/dist/public'),
                         ('scp', 'jarn.com:/var/dist/public'))

    def testUserOnly(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.to_ssh_url('scp://stefan@/var/dist/public'),
                         ('scp', 'stefan@:/var/dist/public'))

    def testWhitespace(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.to_ssh_url(' ssh://stefan@jarn.com/var/dist/public'),
                         ('', ' ssh://stefan@jarn.com/var/dist/public'))

    def testEmptyString(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.to_ssh_url(''), ('', ''))


class AbspathTests(unittest.TestCase):

    def testFile(self):
        urlparser = URLParser()
        cwd = os.getcwd()
        self.assertEqual(urlparser.abspath('file://%s/var/dist/public' % cwd),
                         'file://%s/var/dist/public' % cwd)

    def testRelativeFile(self):
        urlparser = URLParser()
        cwd = os.getcwd()
        self.assertEqual(urlparser.abspath('file:var/dist/public'),
                         'file://%s/var/dist/public' % cwd)

    def testExpandUser(self):
        urlparser = URLParser()
        logname = os.environ.get('LOGNAME')
        home = os.environ.get('HOME')
        self.assertEqual(urlparser.abspath('file:~%s/public' % logname),
                         'file://%s/public' % home)

    def testLocalhost(self):
        urlparser = URLParser()
        cwd = os.getcwd()
        self.assertEqual(urlparser.abspath('file://localhost%s/var/dist/public' % cwd),
                         'file://localhost%s/var/dist/public' % cwd)

    def testLocalhostExpandUser(self):
        urlparser = URLParser()
        logname = os.environ.get('LOGNAME')
        home = os.environ.get('HOME')
        self.assertEqual(urlparser.abspath('file://localhost/~%s/public' % logname),
                         'file://localhost%s/public' % home)

    def testNonFile(self):
        urlparser = URLParser()
        self.assertEqual(urlparser.abspath('svn://jarn.com/public'),
                         'svn://jarn.com/public')

