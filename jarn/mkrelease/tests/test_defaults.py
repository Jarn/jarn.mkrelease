import unittest

from jarn.mkrelease.mkrelease import Defaults

from jarn.mkrelease.testing import JailSetup
from jarn.mkrelease.testing import quiet


class DefaultsTests(JailSetup):

    def test_defaults_defaults(self):
        self.mkfile('my.cfg', """
[mkrelease]
""")
        defaults = Defaults('my.cfg')
        self.assertEqual(defaults.distbase, '')
        self.assertEqual(defaults.distdefault, [])
        self.assertEqual(defaults.commit, True)
        self.assertEqual(defaults.tag, True)
        self.assertEqual(defaults.register, True)
        self.assertEqual(defaults.upload, True)
        self.assertEqual(defaults.sign, False)
        self.assertEqual(defaults.push, False)
        self.assertEqual(defaults.develop, False)
        self.assertEqual(defaults.quiet, False)
        self.assertEqual(defaults.identity, '')
        self.assertEqual(defaults.formats, [])
        self.assertEqual(defaults.aliases, {})
        #self.assertEqual(defaults.servers, {})

    @quiet
    def test_empty_defaults(self):
        self.mkfile('my.cfg', """
[mkrelease]
distbase =
distdefault =
commit =
tag =
register =
upload =
sign =
push =
develop =
quiet =
identity =
formats =
[aliases]
""")
        defaults = Defaults('my.cfg')
        self.assertEqual(defaults.distbase, '')
        self.assertEqual(defaults.distdefault, [])
        self.assertEqual(defaults.commit, True)
        self.assertEqual(defaults.tag, True)
        self.assertEqual(defaults.register, True)
        self.assertEqual(defaults.upload, True)
        self.assertEqual(defaults.sign, False)
        self.assertEqual(defaults.push, False)
        self.assertEqual(defaults.develop, False)
        self.assertEqual(defaults.quiet, False)
        self.assertEqual(defaults.identity, '')
        self.assertEqual(defaults.formats, [])
        self.assertEqual(defaults.aliases, {})
        #self.assertEqual(defaults.servers, {})

    def test_read_defaults(self):
        self.mkfile('my.cfg', """
[mkrelease]
distbase = bedrock.com:
distdefault = public
commit = false
tag = 0
register = no
upload = off
sign = true
push = 1
develop = yes
quiet = on
identity = fred@bedrock.com
formats = zip wheel
[aliases]
public = bedrock.com:eggs
""")
        defaults = Defaults('my.cfg')
        self.assertEqual(defaults.distbase, 'bedrock.com:')
        self.assertEqual(defaults.distdefault, ['public'])
        self.assertEqual(defaults.commit, False)
        self.assertEqual(defaults.tag, False)
        self.assertEqual(defaults.register, False)
        self.assertEqual(defaults.upload, False)
        self.assertEqual(defaults.sign, True)
        self.assertEqual(defaults.push, True)
        self.assertEqual(defaults.develop, True)
        self.assertEqual(defaults.quiet, True)
        self.assertEqual(defaults.identity, 'fred@bedrock.com')
        self.assertEqual(defaults.formats, ['zip', 'wheel'])
        self.assertEqual(defaults.aliases, {'public': ['bedrock.com:eggs']})
        #self.assertEqual(defaults.servers, {})


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

