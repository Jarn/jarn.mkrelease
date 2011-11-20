import unittest

from jarn.mkrelease.configparser import ConfigParser

from jarn.mkrelease.testing import JailSetup


class ConfigParserTests(JailSetup):

    def test_simple(self):
        self.mkfile('my.cfg', """
[section]
s_val = fred
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(parser.get('section', 's_val'), 'fred')
        self.assertEqual(parser.getlist('section', 's_val'), ['fred'])
        self.assertEqual(parser.getstring('section', 's_val'), 'fred')
        self.assertEqual(parser.getboolean('section', 's_val'), None)
        self.assertEqual(parser.getint('section', 's_val'), None)
        self.assertEqual(parser.getfloat('section', 's_val'), None)

    def test_bad_format(self):
        self.mkfile('my.cfg', """
this = wrong
[section]
s_val = fred
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(parser.get('section', 's_val'), None)
        self.assertEqual(parser.getlist('section', 's_val'), None)
        self.assertEqual(parser.getstring('section', 's_val'), None)
        self.assertEqual(parser.getboolean('section', 's_val'), None)
        self.assertEqual(parser.getint('section', 's_val'), None)
        self.assertEqual(parser.getfloat('section', 's_val'), None)

    def test_missing_option(self):
        self.mkfile('my.cfg', """
[section]
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(parser.get('section', 's_val'), None)
        self.assertEqual(parser.getlist('section', 's_val'), None)
        self.assertEqual(parser.getstring('section', 's_val'), None)
        self.assertEqual(parser.getboolean('section', 's_val'), None)
        self.assertEqual(parser.getint('section', 's_val'), None)
        self.assertEqual(parser.getfloat('section', 's_val'), None)

    def test_empty_value(self):
        self.mkfile('my.cfg', """
[section]
e_val =
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(parser.get('section', 'e_val'), '')
        self.assertEqual(parser.getlist('section', 'e_val'), [])
        self.assertEqual(parser.getstring('section', 'e_val'), '')
        self.assertEqual(parser.getboolean('section', 'e_val'), None)
        self.assertEqual(parser.getint('section', 'e_val'), None)
        self.assertEqual(parser.getfloat('section', 'e_val'), None)

    def test_with_spaces(self):
        self.mkfile('my.cfg', """
[section]
m_val = fred flintstone
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(parser.get('section', 'm_val'), 'fred flintstone')
        self.assertEqual(parser.getlist('section', 'm_val'), ['fred', 'flintstone'])
        self.assertEqual(parser.getstring('section', 'm_val'), None)
        self.assertEqual(parser.getboolean('section', 'm_val'), None)
        self.assertEqual(parser.getint('section', 'm_val'), None)
        self.assertEqual(parser.getfloat('section', 'm_val'), None)

    def test_with_newlines(self):
        self.mkfile('my.cfg', """
[section]
m_val =
    fred
    flintstone
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(parser.get('section', 'm_val'), '\nfred\nflintstone')
        self.assertEqual(parser.getlist('section', 'm_val'), ['fred', 'flintstone'])
        self.assertEqual(parser.getstring('section', 'm_val'), None)
        self.assertEqual(parser.getboolean('section', 'm_val'), None)
        self.assertEqual(parser.getint('section', 'm_val'), None)
        self.assertEqual(parser.getfloat('section', 'm_val'), None)

    def test_boolean(self):
        self.mkfile('my.cfg', """
[section]
b_val = yes
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(parser.get('section', 'b_val'), 'yes')
        self.assertEqual(parser.getlist('section', 'b_val'), ['yes'])
        self.assertEqual(parser.getstring('section', 'b_val'), 'yes')
        self.assertEqual(parser.getboolean('section', 'b_val'), True)
        self.assertEqual(parser.getint('section', 'b_val'), None)
        self.assertEqual(parser.getfloat('section', 'b_val'), None)

    def test_int(self):
        self.mkfile('my.cfg', """
[section]
i_val = 10
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(parser.get('section', 'i_val'), '10')
        self.assertEqual(parser.getlist('section', 'i_val'), ['10'])
        self.assertEqual(parser.getstring('section', 'i_val'), '10')
        self.assertEqual(parser.getboolean('section', 'i_val'), None)
        self.assertEqual(parser.getint('section', 'i_val'), 10)
        self.assertEqual(parser.getfloat('section', 'i_val'), 10.0)

    def test_float(self):
        self.mkfile('my.cfg', """
[section]
f_val = 0.1
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(parser.get('section', 'f_val'), '0.1')
        self.assertEqual(parser.getlist('section', 'f_val'), ['0.1'])
        self.assertEqual(parser.getstring('section', 'f_val'), '0.1')
        self.assertEqual(parser.getboolean('section', 'f_val'), None)
        self.assertEqual(parser.getint('section', 'f_val'), None)
        self.assertEqual(parser.getfloat('section', 'f_val'), 0.1)


class WarnFuncTests(JailSetup):

    def test_warn_bad_format(self):
        self.mkfile('my.cfg', """
this = wrong
[section]
s_val = fred
""")
        parser = ConfigParser()
        self.assertEqual(len(parser.warnings), 0)
        parser.read('my.cfg')
        self.assertEqual(len(parser.warnings), 1)

    def test_warn_string_multi(self):
        self.mkfile('my.cfg', """
[section]
s_val = fred flintstone
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(len(parser.warnings), 0)
        self.assertEqual(parser.getstring('section', 's_val'), None)
        self.assertEqual(len(parser.warnings), 1)

    def test_warn_boolean_multi(self):
        self.mkfile('my.cfg', """
[section]
b_val = yes no
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(len(parser.warnings), 0)
        self.assertEqual(parser.getboolean('section', 'b_val'), None)
        self.assertEqual(len(parser.warnings), 1)

    def test_warn_boolean_value(self):
        self.mkfile('my.cfg', """
[section]
b_val = x
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(len(parser.warnings), 0)
        self.assertEqual(parser.getboolean('section', 'b_val'), None)
        self.assertEqual(len(parser.warnings), 1)

    def test_warn_int_multi(self):
        self.mkfile('my.cfg', """
[section]
i_val = 1 2
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(len(parser.warnings), 0)
        self.assertEqual(parser.getint('section', 'i_val'), None)
        self.assertEqual(len(parser.warnings), 1)

    def test_warn_int_value(self):
        self.mkfile('my.cfg', """
[section]
i_val = x
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(len(parser.warnings), 0)
        self.assertEqual(parser.getint('section', 'i_val'), None)
        self.assertEqual(len(parser.warnings), 1)

    def test_warn_float_multi(self):
        self.mkfile('my.cfg', """
[section]
f_val = 0.1 0.2
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(len(parser.warnings), 0)
        self.assertEqual(parser.getfloat('section', 'f_val'), None)
        self.assertEqual(len(parser.warnings), 1)

    def test_warn_float_value(self):
        self.mkfile('my.cfg', """
[section]
f_val = x
""")
        parser = ConfigParser()
        parser.read('my.cfg')
        self.assertEqual(len(parser.warnings), 0)
        self.assertEqual(parser.getfloat('section', 'f_val'), None)
        self.assertEqual(len(parser.warnings), 1)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

