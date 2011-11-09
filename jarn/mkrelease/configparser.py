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
                warn(e)
        return default

    def getint(self, section, option, default=None):
        if self.has_option(section, option):
            try:
                return super(ConfigParser, self).getint(section, option)
            except ValueError, e:
                warn(e)
        return default

    def getfloat(self, section, option, default=None):
        if self.has_option(section, option):
            try:
                return super(ConfigParser, self).getfloat(section, option)
            except ValueError, e:
                warn(e)
        return default

