import unittest

from jarn.mkrelease.mkrelease import Locations

from jarn.mkrelease.testing import quiet


class defaults:
    distbase = ''
    distdefault = ''
    aliases = {}
    servers = {}

    def __init__(self, distbase='', distdefault='', aliases=None, servers=None):
        self.distbase = distbase
        self.distdefault = distdefault
        self.aliases = {} if aliases is None else aliases
        self.servers = {} if servers is None else servers


class HasHostTests(unittest.TestCase):

    def test_simple(self):
        locations = Locations(defaults)
        self.assertEqual(locations.has_host('foo:bar'), True)

    def test_slash(self):
        locations = Locations(defaults)
        self.assertEqual(locations.has_host('foo:bar/baz'), True)

    def test_no_colon(self):
        locations = Locations(defaults)
        self.assertEqual(locations.has_host('foo/bar/baz'), False)

    def test_slash_before_colon(self):
        locations = Locations(defaults)
        self.assertEqual(locations.has_host('foo/bar:baz'), False)


class JoinTests(unittest.TestCase):

    def test_simple(self):
        locations = Locations(defaults)
        self.assertEqual(locations.join('foo:', 'bar'), 'foo:bar')

    def test_slash(self):
        locations = Locations(defaults)
        self.assertEqual(locations.join('foo:/', 'bar'), 'foo:/bar')

    def test_inserted_slash(self):
        locations = Locations(defaults)
        self.assertEqual(locations.join('foo:/bar', 'baz'), 'foo:/bar/baz')


class GetLocationTests(unittest.TestCase):

    def test_simple(self):
        locations = Locations(defaults)
        self.assertEqual(locations.get_location('foo'), ['foo'])

    def test_empty(self):
        locations = Locations(defaults)
        self.assertEqual(locations.get_location(None), [])
        self.assertEqual(locations.get_location(''), [])

    def test_distbase(self):
        locations = Locations(defaults(distbase='jarn.com:eggs'))
        self.assertEqual(locations.get_location('foo'), ['jarn.com:eggs/foo'])

    def test_has_host(self):
        locations = Locations(defaults(distbase='jarn.com:eggs'))
        self.assertEqual(locations.get_location('jarn.com:foo'), ['jarn.com:foo'])

    def test_is_url(self):
        locations = Locations(defaults(distbase='jarn.com:eggs'))
        self.assertEqual(locations.get_location('http://jarn.com'), ['http://jarn.com'])
        self.assertEqual(locations.get_location('ssh://jarn.com'), ['ssh://jarn.com'])

    def test_is_server(self):
        locations = Locations(defaults(distbase='jarn.com:eggs', servers={'pypi': None}))
        self.assertEqual(locations.get_location('pypi'), ['pypi'])

    def test_pypi_is_server(self):
        locations = Locations(defaults(distbase='jarn.com:eggs'))
        self.assertEqual(locations.get_location('pypi'), ['pypi'])

    def test_alias(self):
        locations = Locations(defaults(aliases={'foo': ['bar']}))
        self.assertEqual(locations.get_location('foo'), ['bar'])

    def test_alias_recursive(self):
        locations = Locations(defaults(aliases={'foo': ['bar'], 'bar': ['baz']}))
        self.assertEqual(locations.get_location('foo'), ['baz'])

    @quiet
    def test_alias_infinite_loop(self):
        locations = Locations(defaults(aliases={'foo': ['bar'], 'bar': ['foo']}))
        self.assertRaises(SystemExit, locations.get_location, 'foo')

    def test_alias_fan_out(self):
        aliases = {
            'one': ['two', 'three'],
            'two': ['four', 'five', 'six'],
            'five': ['seven', 'eight'],
        }
        locations = Locations(defaults(aliases=aliases))
        self.assertEqual(locations.get_location('one'), ['four', 'seven', 'eight', 'six', 'three'])


class GetDefaultLocationTests(unittest.TestCase):

    def test_default_location(self):
        locations = Locations(defaults(distdefault=['foo']))
        self.assertEqual(locations.get_default_location(), ['foo'])

    def test_empty_default_location(self):
        locations = Locations(defaults)
        self.assertEqual(locations.get_default_location(), [])

    def test_multi_default_location(self):
        locations = Locations(defaults(distdefault=['foo', 'bar']))
        self.assertEqual(locations.get_default_location(), ['foo', 'bar'])

    def test_alias_default_location(self):
        aliases = {
            'one': ['two', 'three'],
            'three': ['four']
        }
        locations = Locations(defaults(distdefault=['one'], aliases=aliases))
        self.assertEqual(locations.get_default_location(), ['two', 'four'])


class CheckLocationsTests(unittest.TestCase):

    @quiet
    def test_check_empty_locations(self):
        locations = Locations(defaults)
        self.assertRaises(SystemExit, locations.check_empty_locations)
        self.assertRaises(SystemExit, locations.check_empty_locations, [])
        locations.extend(['foo'])
        locations.check_empty_locations()
        locations.check_empty_locations(['bar'])
        self.assertRaises(SystemExit, locations.check_empty_locations, [])

    @quiet
    def test_check_valid_locations(self):
        locations = Locations(defaults(servers={'pypi': None}))
        locations.check_valid_locations()
        locations.check_valid_locations([])
        locations.check_valid_locations(['pypi'])
        locations.check_valid_locations(['jarn.com:eggs'])
        locations.check_valid_locations(['sftp://jarn.com/home/stefan/eggs'])
        locations.check_valid_locations(['scp://jarn.com/home/stefan/eggs'])
        locations.extend(['foo'])
        self.assertRaises(SystemExit, locations.check_valid_locations)
        self.assertRaises(SystemExit, locations.check_valid_locations, ['bar'])
        self.assertRaises(SystemExit, locations.check_valid_locations, ['http://jarn.com'])
        self.assertRaises(SystemExit, locations.check_valid_locations, ['ssh://jarn.com'])
        self.assertRaises(SystemExit, locations.check_valid_locations, ['scp://'])

