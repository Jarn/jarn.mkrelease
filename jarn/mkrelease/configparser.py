import sys

if sys.version_info[:2] >= (3, 2):
    from configparser import Error
    from configparser import ConfigParser as _BaseParser
elif sys.version_info[0] >= 3:
    from configparser import Error
    from configparser import SafeConfigParser as _BaseParser
else:
    from ConfigParser import Error
    from ConfigParser import SafeConfigParser as _BaseParser


class MultipleValueError(Error):
    pass


class errors2warnings(object):
    """Turn ConfigParser.Errors into warnings."""

    def __init__(self, parser):
        self.parser = parser

    def __enter__(self):
        pass

    def __exit__(self, type, value, tb):
        if isinstance(value, Error):
            self.parser.warn(str(value))
            return True


class ConfigParser(_BaseParser, object):

    def __init__(self, warn_func=None, raw=True):
        super(ConfigParser, self).__init__()
        self.warnings = []
        self.warn_func = warn_func
        self.raw = raw
        # Python < 3.2
        if hasattr(self, '_boolean_states'):
            self.BOOLEAN_STATES = self._boolean_states

    def warn(self, msg):
        self.warnings.append(msg)
        if self.warn_func is not None:
            self.warn_func(msg)

    def read(self, filenames):
        self.warnings = []
        with errors2warnings(self):
            super(ConfigParser, self).read(filenames)

    def items(self, section, default=None):
        if self.has_section(section):
            with errors2warnings(self):
                value = super(ConfigParser, self).items(section, raw=self.raw)
                return value
        return default

    def get(self, section, option, default=None):
        if self.has_option(section, option):
            with errors2warnings(self):
                value = super(ConfigParser, self).get(section, option, raw=self.raw)
                return value
        return default

    def getlist(self, section, option, default=None):
        if self.has_option(section, option):
            with errors2warnings(self):
                value = super(ConfigParser, self).get(section, option, raw=self.raw)
                return self.to_list(value)
        return default

    def getstring(self, section, option, default=None):
        if self.has_option(section, option):
            with errors2warnings(self):
                value = super(ConfigParser, self).get(section, option, raw=self.raw)
                try:
                    return self.to_string(value)
                except MultipleValueError as e:
                    self.warn("Multiple values not allowed: %s = %r" % (option, self._value_from_exc(e)))
        return default

    def getboolean(self, section, option, default=None):
        if self.has_option(section, option):
            with errors2warnings(self):
                value = super(ConfigParser, self).get(section, option, raw=self.raw)
                try:
                    return self.to_boolean(value)
                except MultipleValueError as e:
                    self.warn("Multiple values not allowed: %s = %r" % (option, self._value_from_exc(e)))
                except ValueError as e:
                    self.warn('Not a boolean: %s = %r' % (option, self._value_from_exc(e)))
        return default

    def getint(self, section, option, default=None):
        if self.has_option(section, option):
            with errors2warnings(self):
                value = super(ConfigParser, self).get(section, option, raw=self.raw)
                try:
                    return self.to_int(value)
                except MultipleValueError as e:
                    self.warn('Multiple values not allowed: %s = %r' % (option, self._value_from_exc(e)))
                except ValueError as e:
                    self.warn('Not an integer: %s = %r' % (option, self._value_from_exc(e)))
        return default

    def getfloat(self, section, option, default=None):
        if self.has_option(section, option):
            with errors2warnings(self):
                value = super(ConfigParser, self).get(section, option, raw=self.raw)
                try:
                    return self.to_float(value)
                except MultipleValueError as e:
                    self.warn('Multiple values not allowed: %s = %r' % (option, self._value_from_exc(e)))
                except ValueError as e:
                    self.warn('Not a float: %s = %r' % (option, self._value_from_exc(e)))
        return default

    def to_list(self, value):
        return value.split()

    def to_string(self, value):
        v = self._single_value(value)
        return v

    def to_boolean(self, value):
        v = self._single_value(value).lower()
        if v not in self.BOOLEAN_STATES:
            raise ValueError('Not a boolean: %s' % v)
        return self.BOOLEAN_STATES[v]

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

