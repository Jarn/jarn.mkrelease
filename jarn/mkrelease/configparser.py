from ConfigParser import SafeConfigParser
from ConfigParser import Error


class MultipleValueError(Error):
    pass


class ConfigParser(SafeConfigParser, object):

    def __init__(self, warn_func=None):
        super(ConfigParser, self).__init__()
        self.warnings = []
        self.warn_func = warn_func

    def warn(self, msg):
        self.warnings.append(msg)
        if self.warn_func is not None:
            self.warn_func(msg)

    def read(self, filenames):
        self.warnings = []
        try:
            super(ConfigParser, self).read(filenames)
        except Error, e:
            self.warn(str(e))

    def get(self, section, option, default=None):
        if self.has_option(section, option):
            value = super(ConfigParser, self).get(section, option)
            return value
        return default

    def getlist(self, section, option, default=None):
        if self.has_option(section, option):
            value = super(ConfigParser, self).get(section, option)
            return self.to_list(value)
        return default

    def getstring(self, section, option, default=None):
        if self.has_option(section, option):
            value = super(ConfigParser, self).get(section, option)
            try:
                return self.to_string(value)
            except MultipleValueError, e:
                self.warn("Multiple values not allowed: %s = %r" % (option, self._value_from_exc(e)))
        return default

    def getboolean(self, section, option, default=None):
        if self.has_option(section, option):
            value = super(ConfigParser, self).get(section, option)
            try:
                return self.to_boolean(value)
            except MultipleValueError, e:
                self.warn("Multiple values not allowed: %s = %r" % (option, self._value_from_exc(e)))
            except ValueError, e:
                self.warn('Not a boolean: %s = %r' % (option, self._value_from_exc(e)))
        return default

    def getint(self, section, option, default=None):
        if self.has_option(section, option):
            value = super(ConfigParser, self).get(section, option)
            try:
                return self.to_int(value)
            except MultipleValueError, e:
                self.warn('Multiple values not allowed: %s = %r' % (option, self._value_from_exc(e)))
            except ValueError, e:
                self.warn('Not an integer: %s = %r' % (option, self._value_from_exc(e)))
        return default

    def getfloat(self, section, option, default=None):
        if self.has_option(section, option):
            value = super(ConfigParser, self).get(section, option)
            try:
                return self.to_float(value)
            except MultipleValueError, e:
                self.warn('Multiple values not allowed: %s = %r' % (option, self._value_from_exc(e)))
            except ValueError, e:
                self.warn('Not a float: %s = %r' % (option, self._value_from_exc(e)))
        return default

    def to_list(self, value):
        return value.split()

    def to_string(self, value):
        v = self._single_value(value)
        return v

    def to_boolean(self, value):
        v = self._single_value(value).lower()
        if v not in self._boolean_states:
            raise ValueError('Not a boolean: %s' % v)
        return self._boolean_states[v]

    def to_int(self, value):
        v = self._single_value(value)
        return int(v)

    def to_float(self, value):
        v = self._single_value(value)
        return float(v)

    def _single_value(self, value):
        v = value.strip()
        if len(v.split()) > 1:
            raise MultipleValueError('Multiple values not allowed: %s' % v)
        return v

    def _value_from_exc(self, exc):
        # e.g.: invalid literal for int() with base 10: 'a'
        msg = str(exc)
        colon = msg.find(':')
        if colon >= 0:
            value = msg[colon+1:].lstrip()
            if (value.startswith("'") and value.endswith("'")) or \
               (value.startswith('"') and value.endswith('"')):
                value = value[1:-1]
            return value
        return ''


del SafeConfigParser
