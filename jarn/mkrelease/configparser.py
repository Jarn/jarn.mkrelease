from ConfigParser import SafeConfigParser
from exit import warn


class ConfigParser(SafeConfigParser, object):

    def get(self, section, option, default=None):
        if self.has_option(section, option):
            return super(ConfigParser, self).get(section, option)
        return default

    def getboolean(self, section, option, default=None):
        if self.has_option(section, option):
            try:
                return super(ConfigParser, self).getboolean(section, option)
            except ValueError, e:
                warn('Not a boolean: %s = %s' % (option, self._value_from_exc(e)))
        return default

    def getint(self, section, option, default=None):
        if self.has_option(section, option):
            try:
                return super(ConfigParser, self).getint(section, option)
            except ValueError, e:
                warn('Not an integer: %s = %s' % (option, self._value_from_exc(e)))
        return default

    def getfloat(self, section, option, default=None):
        if self.has_option(section, option):
            try:
                return super(ConfigParser, self).getfloat(section, option)
            except ValueError, e:
                warn('Not a float: %s = %s' % (option, self._value_from_exc(e)))
        return default

    def _value_from_exc(self, exc):
        # e.g.: invalid literal for int() with base 10: 'foo'
        msg = str(exc)
        colon = msg.find(':')
        if colon >= 0:
            value = msg[colon+1:].strip()
            if (value.startswith("'") and value.endswith("'")) or \
               (value.startswith('"') and value.endswith('"')):
                value = value[1:-1]
            return value
        return ''

