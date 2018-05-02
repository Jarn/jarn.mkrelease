import sys
import re

if sys.version_info[:2] >= (3, 2):
    from configparser import Error
    from configparser import MissingSectionHeaderError
    from configparser import ConfigParser as _BaseParser
elif sys.version_info[0] >= 3:
    from configparser import Error
    from configparser import MissingSectionHeaderError
    from configparser import SafeConfigParser as _BaseParser
else:
    from ConfigParser import Error
    from ConfigParser import MissingSectionHeaderError
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
        if isinstance(value, MissingSectionHeaderError):
            self._reformat_exception(value)
        if isinstance(value, Error):
            self.parser.warn(str(value))
            return True

    def _reformat_exception(self, value):
        value.message = 'File contains no section headers: %r\n\t[line %2d]: %r' % (
            value.source if sys.version_info >= (3, 2) else value.filename,
            value.lineno,
            value.line)


class ConfigParser(object):

    def __init__(self, warn_func=None, raw=True):
        self.warnings = []
        self.warn_func = warn_func
        self.raw = raw
        self._valid = False
        self._base = _BaseParser()
        self._base.optionxform = lambda x: x.lower().replace('-', '_')
        # Python < 3.2
        if hasattr(self._base, '_boolean_states'):
            self._base.BOOLEAN_STATES = self._base._boolean_states

    def warn(self, msg):
        self.warnings.append(msg)
        if self.warn_func is not None:
            self.warn_func(msg)

    def read(self, filenames):
        self.warnings = []
        with errors2warnings(self):
            self._base.read(filenames)
        self._valid = not self.warnings
        return self._valid

    def has_section(self, section):
        return self._base.has_section(section) and self._valid

    def has_option(self, section, option):
        return self._base.has_option(section, option) and self._valid

    def sections(self, default=None):
        return self._base.sections() if self._valid else default

    def options(self, section, default=None):
        return self._base.options(section) if self._valid else default

    def items(self, section, default=None):
        if self.has_section(section):
            with errors2warnings(self):
                value = self._base.items(section, raw=self.raw)
                return value
        return default

    def get(self, section, option, default=None):
        if self.has_option(section, option):
            with errors2warnings(self):
                value = self._base.get(section, option, raw=self.raw)
                return value
        return default

    def getlist(self, section, option, default=None):
        if self.has_option(section, option):
            with errors2warnings(self):
                value = self._base.get(section, option, raw=self.raw)
                return self.to_list(value)
        return default

    def getstring(self, section, option, default=None):
        if self.has_option(section, option):
            with errors2warnings(self):
                value = self._base.get(section, option, raw=self.raw)
                try:
                    return self.to_string(value)
                except MultipleValueError as e:
                    self.warn("Multiple values not allowed: %s = %r" % (option, self._value_from_exc(e)))
        return default

    def getboolean(self, section, option, default=None):
        if self.has_option(section, option):
            with errors2warnings(self):
                value = self._base.get(section, option, raw=self.raw)
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
                value = self._base.get(section, option, raw=self.raw)
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
                value = self._base.get(section, option, raw=self.raw)
                try:
                    return self.to_float(value)
                except MultipleValueError as e:
                    self.warn('Multiple values not allowed: %s = %r' % (option, self._value_from_exc(e)))
                except ValueError as e:
                    self.warn('Not a float: %s = %r' % (option, self._value_from_exc(e)))
        return default

    def to_list(self, value):
        v = re.split(r',\s*|\s+', value)
        return [x for x in v if x]

    def to_string(self, value):
        v = self._single_value(value)
        return v

    def to_boolean(self, value):
        v = self._single_value(value).lower()
        if v not in self._base.BOOLEAN_STATES:
            raise ValueError('Not a boolean: %s' % v)
        return self._base.BOOLEAN_STATES[v]

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

