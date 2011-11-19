from ConfigParser import SafeConfigParser
from ConfigParser import Error
from exit import warn


class MultipleValueError(Error):
    pass


class ConfigParser(SafeConfigParser, object):

    def read(self, filenames):
        try:
            super(ConfigParser, self).read(filenames)
        except Error, e:
            warn(e)

    def get(self, section, option, default=None):
        if self.has_option(section, option):
            return super(ConfigParser, self).get(section, option)
        return default

    def getstring(self, section, option, default=None):
        if self.has_option(section, option):
            value = super(ConfigParser, self).get(section, option)
            try:
                return self.to_string(value)
            except MultipleValueError, e:
                warn("Multiple values not allowed: %s = %r" % (option, self._value_from_exc(e)))
        return default

    def getlist(self, section, option, default=None):
        if self.has_option(section, option):
            value = super(ConfigParser, self).get(section, option)
            return self.to_list(value)
        return default

    def getboolean(self, section, option, default=None):
        if self.has_option(section, option):
            value = super(ConfigParser, self).get(section, option)
            try:
                return self.to_boolean(value)
            except MultipleValueError, e:
                warn("Multiple values not allowed: %s = %r" % (option, self._value_from_exc(e)))
            except ValueError, e:
                warn('Not a boolean: %s = %r' % (option, self._value_from_exc(e)))
        return default

    def getint(self, section, option, default=None):
        if self.has_option(section, option):
            value = super(ConfigParser, self).get(section, option)
            try:
                return self.to_int(value)
            except MultipleValueError, e:
                warn('Multiple values not allowed: %s = %r' % (option, self._value_from_exc(e)))
            except ValueError, e:
                warn('Not an integer: %s = %r' % (option, self._value_from_exc(e)))
        return default

    def getfloat(self, section, option, default=None):
        if self.has_option(section, option):
            value = super(ConfigParser, self).get(section, option)
            try:
                return self.to_float(value)
            except MultipleValueError, e:
                warn('Multiple values not allowed: %s = %r' % (option, self._value_from_exc(e)))
            except ValueError, e:
                warn('Not a float: %s = %r' % (option, self._value_from_exc(e)))
        return default

    def to_string(self, value):
        return self.single_value(value)

    def to_list(self, value):
        return value.split()

    def to_boolean(self, value):
        v = self.single_value(value).lower()
        if v not in self._boolean_states:
            raise ValueError('Not a boolean: %s' % value)
        return self._boolean_states[v]

    def to_int(self, value):
        v = self.single_value(value)
        return int(v)

    def to_float(self, value):
        v = self.single_value(value)
        return float(v)

    def single_value(self, value):
        v = value.strip()
        if len(v.split()) > 1:
            raise MultipleValueError('Multiple values not allowed: %s' % value)
        return v

    def _value_from_exc(self, exc):
        # e.g.: invalid literal for int() with base 10: 'a'
        msg = str(exc)
        colon = msg.find(':')
        if colon >= 0:
            value = msg[colon+1:].lstrip(' \t')
            if (value.startswith("'") and value.endswith("'")) or \
               (value.startswith('"') and value.endswith('"')):
                value = value[1:-1]
            return value
        return ''

