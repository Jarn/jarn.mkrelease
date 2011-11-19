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

    def getboolean(self, section, option, default=None):
        if self.has_option(section, option):
            value = super(ConfigParser, self).get(section, option)
            try:
                return self._to_boolean(value)
            except MultipleValueError, e:
                warn("Multiple values not allowed: %s = %r" % (option, self._value_from_exc(e)))
            except ValueError, e:
                warn('Not a boolean: %s = %r' % (option, self._value_from_exc(e)))
        return default

    def getint(self, section, option, default=None):
        if self.has_option(section, option):
            value = super(ConfigParser, self).get(section, option)
            try:
                return self._to_int(value)
            except MultipleValueError, e:
                warn('Multiple values not allowed: %s = %r' % (option, self._value_from_exc(e)))
            except ValueError, e:
                warn('Not an integer: %s = %r' % (option, self._value_from_exc(e)))
        return default

    def getfloat(self, section, option, default=None):
        if self.has_option(section, option):
            value = super(ConfigParser, self).get(section, option)
            try:
                return self._to_float(value)
            except MultipleValueError, e:
                warn('Multiple values not allowed: %s = %r' % (option, self._value_from_exc(e)))
            except ValueError, e:
                warn('Not a float: %s = %r' % (option, self._value_from_exc(e)))
        return default

    def _convertable(self, value):
        v = value.lower().strip()
        if len(v.split()) > 1:
            raise MultipleValueError('Multiple values not allowed: %s' % value)
        return v

    def _to_boolean(self, value):
        v = self._convertable(value)
        if v not in self._boolean_states:
            raise ValueError('Not a boolean: %s' % value)
        return self._boolean_states[v]

    def _to_int(self, value):
        return int(self._convertable(value))

    def _to_float(self, value):
        return float(self._convertable(value))

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

