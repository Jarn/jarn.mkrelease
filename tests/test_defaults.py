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
        self.assertEqual(defaults.register, False)
        self.assertEqual(defaults.upload, True)
        self.assertEqual(defaults.sign, False)
        self.assertEqual(defaults.manifest, False)
        self.assertEqual(defaults.push, True)
        self.assertEqual(defaults.develop, False)
        self.assertEqual(defaults.quiet, False)
        self.assertEqual(defaults.identity, '')
        self.assertEqual(defaults.formats, [])
        self.assertEqual(defaults.aliases, {})
        #self.assertEqual(defaults.servers, {})
        self.assertEqual(defaults.twine, '')
        self.assertEqual(defaults.interactive, True)

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
manifest-only =
develop =
quiet =
identity =
formats =
twine =
interactive =
[aliases]
""")
        defaults = Defaults('my.cfg')
        self.assertEqual(defaults.distbase, '')
        self.assertEqual(defaults.distdefault, [])
        self.assertEqual(defaults.commit, True)
        self.assertEqual(defaults.tag, True)
        self.assertEqual(defaults.register, False)
        self.assertEqual(defaults.upload, True)
        self.assertEqual(defaults.sign, False)
        self.assertEqual(defaults.manifest, False)
        self.assertEqual(defaults.push, True)
        self.assertEqual(defaults.develop, False)
        self.assertEqual(defaults.quiet, False)
        self.assertEqual(defaults.identity, '')
        self.assertEqual(defaults.formats, [])
        self.assertEqual(defaults.aliases, {})
        #self.assertEqual(defaults.servers, {})
        self.assertEqual(defaults.twine, '')
        self.assertEqual(defaults.interactive, True)

    def test_read_defaults(self):
        self.mkfile('my.cfg', """
[mkrelease]
distbase = bedrock.com:
distdefault = public
commit = false
tag = 0
register = yes
upload = off
sign = true
push = 0
manifest-only = yes
develop = 1
quiet = on
identity = fred@bedrock.com
formats = zip wheel
twine = /usr/local/bin/twine
interactive = FALSE
[aliases]
public = bedrock.com:eggs
""")
        defaults = Defaults('my.cfg')
        self.assertEqual(defaults.distbase, 'bedrock.com:')
        self.assertEqual(defaults.distdefault, ['public'])
        self.assertEqual(defaults.commit, False)
        self.assertEqual(defaults.tag, False)
        self.assertEqual(defaults.register, True)
        self.assertEqual(defaults.upload, False)
        self.assertEqual(defaults.sign, True)
        self.assertEqual(defaults.manifest, True)
        self.assertEqual(defaults.push, False)
        self.assertEqual(defaults.develop, True)
        self.assertEqual(defaults.quiet, True)
        self.assertEqual(defaults.identity, 'fred@bedrock.com')
        self.assertEqual(defaults.formats, ['zip', 'wheel'])
        self.assertEqual(defaults.aliases, {'public': ['bedrock.com:eggs']})
        #self.assertEqual(defaults.servers, {})
        self.assertEqual(defaults.twine, '/usr/local/bin/twine')
        self.assertEqual(defaults.interactive, False)

    def test_dist_location_replaces_distdefault(self):
        self.mkfile('my.cfg', """
[mkrelease]
dist-location = jarn.com:eggs
""")
        defaults = Defaults('my.cfg')
        self.assertEqual(defaults.distdefault, ['jarn.com:eggs'])

    def test_dist_location_overrides_distdefault(self):
        self.mkfile('my.cfg', """
[mkrelease]
distdefault = public
dist-location = jarn.com:eggs
""")
        defaults = Defaults('my.cfg')
        self.assertEqual(defaults.distdefault, ['jarn.com:eggs'])

    def test_pypi_is_server(self):
        self.mkfile('my.cfg', """
[mkrelease]
""")
        defaults = Defaults('my.cfg')
        self.assertTrue('pypi' in defaults.servers)

