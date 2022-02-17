import unittest

from jarn.mkrelease.mkrelease import ReleaseMaker

from jarn.mkrelease.testing import JailSetup
from jarn.mkrelease.testing import quiet


class serverinfo:
    sign = None
    identity = None
    register = None

    def __init__(self, sign=None, identity=None, register=None):
        self.sign = sign
        self.identity = identity
        self.register = register


class GetOptionsTests(JailSetup):

    def test_defaults(self):
        self.mkfile('my.cfg', """\
[mkrelease]
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-d', 'jarn.com:eggs'])
        rm.get_options()
        self.assertEqual(rm.skipcommit, False)
        self.assertEqual(rm.skiptag, False)
        self.assertEqual(rm.skipregister, False)
        self.assertEqual(rm.skipupload, False)
        self.assertEqual(rm.sign, False)
        self.assertEqual(rm.push, True)
        self.assertEqual(rm.develop, False)
        self.assertEqual(rm.quiet, False)
        self.assertEqual(rm.identity, '')
        self.assertEqual(rm.formats, [])
        self.assertNotEqual(rm.distributions, [])
        self.assertNotEqual(rm.infoflags, [])

    def test_dry_run(self):
        self.mkfile('my.cfg', """\
[mkrelease]
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n'])
        rm.get_options()
        self.assertEqual(rm.skipcommit, True)
        self.assertEqual(rm.skiptag, True)
        self.assertEqual(rm.skipregister, True)
        self.assertEqual(rm.skipupload, True)
        self.assertEqual(rm.sign, False)
        self.assertEqual(rm.push, True)
        self.assertEqual(rm.develop, False)
        self.assertEqual(rm.quiet, False)
        self.assertEqual(rm.identity, '')
        self.assertEqual(rm.formats, [])
        self.assertNotEqual(rm.distributions, [])
        self.assertNotEqual(rm.infoflags, [])

    def test_dry_run_from_config(self):
        self.mkfile('my.cfg', """\
[mkrelease]
commit = no
tag = no
register = no
upload = no
""")
        rm = ReleaseMaker(['-c', 'my.cfg'])
        rm.get_options()

        self.assertEqual(rm.skipcommit, True)
        self.assertEqual(rm.skiptag, True)

        rm.defaults.servers.update({'pypi': serverinfo})
        self.assertEqual(rm.get_skipregister('pypi'), True)
        self.assertEqual(rm.get_skipupload(), True)

    def test_register_server_precedence_yes(self):
        # register=yes in server section overrides default
        self.mkfile('my.cfg', """\
[mkrelease]
register = no
upload = yes
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-d', 'jarn.com:eggs'])
        rm.get_options()

        rm.defaults.servers.update({'pypi': serverinfo(register=True)})
        self.assertEqual(rm.get_skipregister('pypi'), False)
        self.assertEqual(rm.get_skipupload(), False)

    def test_register_server_precedence_yes_upload_no(self):
        # register=yes in server section does NOT override default if
        # upload is disabled
        self.mkfile('my.cfg', """\
[mkrelease]
register = no
upload = no
""")
        rm = ReleaseMaker(['-c', 'my.cfg'])     # -d not required
        rm.get_options()

        rm.defaults.servers.update({'pypi': serverinfo(register=True)})
        self.assertEqual(rm.get_skipregister('pypi'), True)
        self.assertEqual(rm.get_skipupload(), True)

    def test_register_server_precedence_yes_upload_flag_no(self):
        # register=yes in server section does NOT override default if
        # -S flag is given
        self.mkfile('my.cfg', """\
[mkrelease]
register = no
upload = yes
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-S'])   # -d not required
        rm.get_options()

        rm.defaults.servers.update({'pypi': serverinfo(register=True)})
        self.assertEqual(rm.get_skipregister('pypi'), True)
        self.assertEqual(rm.get_skipupload(), True)

    def test_register_server_precedence_yes_upload_no_register_flag_no(self):
        # register=yes in server section does NOT override default if
        # -R flag is given
        self.mkfile('my.cfg', """\
[mkrelease]
register = yes
upload = no
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-R'])   # -d not required
        rm.get_options()

        rm.defaults.servers.update({'pypi': serverinfo(register=True)})
        self.assertEqual(rm.get_skipregister('pypi'), True)
        self.assertEqual(rm.get_skipupload(), True)

    def test_register_server_precedence_no(self):
        # register=no in server section overrides default
        self.mkfile('my.cfg', """\
[mkrelease]
register = yes
upload = yes
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-d', 'jarn.com:eggs'])
        rm.get_options()

        rm.defaults.servers.update({'pypi': serverinfo(register=False)})
        self.assertEqual(rm.get_skipregister('pypi'), True)
        self.assertEqual(rm.get_skipupload(), False)

    def test_register_server_precedence_no_upload_no(self):
        # register=no in server section overrides default independent
        # of upload setting
        self.mkfile('my.cfg', """\
[mkrelease]
register = yes
upload = no
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-d', 'jarn.com:eggs'])
        rm.get_options()

        rm.defaults.servers.update({'pypi': serverinfo(register=False)})
        self.assertEqual(rm.get_skipregister('pypi'), True)
        self.assertEqual(rm.get_skipupload(), True)

    def test_register_server_precedence_no_upload_flag_no(self):
        # register=no in server section overrides default independent
        # of upload setting
        self.mkfile('my.cfg', """\
[mkrelease]
register = yes
upload = yes
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-d', 'jarn.com:eggs', '-S'])
        rm.get_options()

        rm.defaults.servers.update({'pypi': serverinfo(register=False)})
        self.assertEqual(rm.get_skipregister('pypi'), True)
        self.assertEqual(rm.get_skipupload(), True)

    def test_build_without_upload(self):
        # -RS makes -d requirement go away
        self.mkfile('my.cfg', """\
[mkrelease]
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-R', '-S']) # -d not required
        rm.get_options()

        self.assertEqual(rm.skipregister, True)
        self.assertEqual(rm.skipupload, True)

    def test_formats(self):
        self.mkfile('my.cfg', """\
[mkrelease]
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n', '-bgwz'])
        rm.get_options()

        self.assertEqual(rm.formats, ['egg', 'gztar', 'wheel', 'zip'])
        self.assertEqual(rm.distributions, [
            ('bdist', ['--formats="egg"']),
            ('sdist', ['--formats="gztar"']),
            ('bdist_wheel', []),
            ('sdist', ['--formats="zip"']),
        ])

    def test_duplicate_formats(self):
        self.mkfile('my.cfg', """\
[mkrelease]
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n', '-zz'])
        rm.get_options()

        self.assertEqual(rm.formats, ['zip', 'zip'])
        self.assertEqual(rm.distributions, [
            ('sdist', ['--formats="zip"']),
            ('sdist', ['--formats="zip"']),
        ])

    def test_formats_from_config(self):
        self.mkfile('my.cfg', """\
[mkrelease]
formats = zip wheel
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n'])
        rm.get_options()

        self.assertEqual(rm.formats, ['zip', 'wheel'])
        self.assertEqual(rm.distributions, [
            ('sdist', ['--formats="zip"']),
            ('bdist_wheel', []),
        ])

    def test_empty_formats_from_config(self):
        self.mkfile('my.cfg', """\
[mkrelease]
formats =
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n'])
        rm.get_options()

        self.assertEqual(rm.formats, [])
        # Fall back to zip
        self.assertEqual(rm.distributions, [('sdist', ['--formats="gztar"']), ('bdist_wheel', [])])

    @quiet
    def test_bad_formats_from_config(self):
        self.mkfile('my.cfg', """\
[mkrelease]
formats = rpm
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n'])
        rm.get_options()

        self.assertEqual(rm.formats, ['rpm'])
        # Fall back to zip
        self.assertEqual(rm.distributions, [('sdist', ['--formats="gztar"']), ('bdist_wheel', [])])

    def test_develop(self):
        self.mkfile('my.cfg', """\
[mkrelease]
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-e', '-d', 'jarn.com:eggs'])
        rm.get_options()

        self.assertEqual(rm.develop, True)
        self.assertEqual(rm.infoflags, [])
        # Implied --no-tag
        self.assertEqual(rm.skiptag, True)

    def test_develop_from_config(self):
        self.mkfile('my.cfg', """\
[mkrelease]
develop = yes
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-d', 'jarn.com:eggs'])
        rm.get_options()

        self.assertEqual(rm.develop, True)
        self.assertEqual(rm.infoflags, [])
        # No implied --no-tag here
        self.assertEqual(rm.skiptag, False)

    def test_misc(self):
        self.mkfile('my.cfg', """\
[mkrelease]
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n', '-pq'])
        rm.get_options()

        self.assertEqual(rm.push, True)
        self.assertEqual(rm.quiet, True)

    def test_misc_from_config(self):
        self.mkfile('my.cfg', """\
[mkrelease]
push = yes
quiet = yes
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n'])
        rm.get_options()

        self.assertEqual(rm.push, True)
        self.assertEqual(rm.quiet, True)

    def test_sign(self):
        self.mkfile('my.cfg', """\
[mkrelease]
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n', '-s'])
        rm.get_options()

        self.assertEqual(rm.sign, True)
        self.assertEqual(rm.identity, '')

        rm.defaults.servers.update({'pypi': serverinfo})
        self.assertEqual(rm.get_uploadflags('pypi'), ['--sign'])

    def test_sign_and_id(self):
        self.mkfile('my.cfg', """\
[mkrelease]
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n', '-s', '-i', 'fred@bedrock.com'])
        rm.get_options()

        self.assertEqual(rm.sign, True)
        self.assertEqual(rm.identity, 'fred@bedrock.com')

        rm.defaults.servers.update({'pypi': serverinfo})
        self.assertEqual(rm.get_uploadflags('pypi'), ['--sign', '--identity="fred@bedrock.com"'])

    def test_id_only(self):
        self.mkfile('my.cfg', """\
[mkrelease]
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n', '-i', 'fred@bedrock.com'])
        rm.get_options()

        self.assertEqual(rm.sign, False)
        self.assertEqual(rm.identity, 'fred@bedrock.com')

        # Implied --sign
        rm.defaults.servers.update({'pypi': serverinfo})
        self.assertEqual(rm.get_uploadflags('pypi'), ['--sign', '--identity="fred@bedrock.com"'])

    def test_sign_from_config(self):
        self.mkfile('my.cfg', """\
[mkrelease]
sign = yes
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n'])
        rm.get_options()

        rm.defaults.servers.update({'pypi': serverinfo})
        self.assertEqual(rm.get_uploadflags('pypi'), ['--sign'])

    def test_sign_and_id_from_config(self):
        self.mkfile('my.cfg', """\
[mkrelease]
sign = yes
identity = fred@bedrock.com
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n'])
        rm.get_options()

        rm.defaults.servers.update({'pypi': serverinfo})
        self.assertEqual(rm.get_uploadflags('pypi'), ['--sign', '--identity="fred@bedrock.com"'])

    def test_id_only_from_config(self):
        self.mkfile('my.cfg', """\
[mkrelease]
identity = fred@bedrock.com
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n'])
        rm.get_options()

        # No implied --sign here
        rm.defaults.servers.update({'pypi': serverinfo})
        self.assertEqual(rm.get_uploadflags('pypi'), [])

    def test_sign_server_precedence_yes(self):
        self.mkfile('my.cfg', """\
[mkrelease]
sign = no
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n'])
        rm.get_options()

        rm.defaults.servers.update({'pypi': serverinfo(sign=True)})
        self.assertEqual(rm.get_uploadflags('pypi'), ['--sign'])

    def test_sign_server_precedence_no(self):
        self.mkfile('my.cfg', """\
[mkrelease]
sign = yes
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n'])
        rm.get_options()

        rm.defaults.servers.update({'pypi': serverinfo(sign=False)})
        self.assertEqual(rm.get_uploadflags('pypi'), [])

    def test_id_server_precedence(self):
        self.mkfile('my.cfg', """\
[mkrelease]
sign = yes
identity = fred@bedrock.com
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-n'])
        rm.get_options()

        rm.defaults.servers.update({'pypi': serverinfo(identity='barney@rubble.com')})
        self.assertEqual(rm.get_uploadflags('pypi'), ['--sign', '--identity="barney@rubble.com"'])

    def test_prefer_manifest(self):
        self.mkfile('my.cfg', """\
[mkrelease]
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-m', '-d', 'jarn.com:eggs'])
        rm.get_options()

        self.assertEqual(rm.manifest, True)

    def test_prefer_manifest_from_config(self):
        self.mkfile('my.cfg', """\
[mkrelease]
manifest-only = yes
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-d', 'jarn.com:eggs'])
        rm.get_options()

        self.assertEqual(rm.manifest, True)

    def test_dist_location(self):
        self.mkfile('my.cfg', """\
[mkrelease]
""")
        rm = ReleaseMaker(['-c', 'my.cfg', '-d', 'jarn.com:eggs'])
        rm.get_options()

        self.assertEqual(rm.locations.locations, ['jarn.com:eggs'])

    def test_dist_location_from_config(self):
        self.mkfile('my.cfg', """\
[mkrelease]
dist-location = jarn.com:eggs
""")
        rm = ReleaseMaker(['-c', 'my.cfg'])
        rm.get_options()

        self.assertEqual(rm.locations.locations, ['jarn.com:eggs'])

