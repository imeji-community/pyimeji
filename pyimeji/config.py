import os
import logging

from appdirs import AppDirs
from six.moves.configparser import RawConfigParser


APP_DIRS = AppDirs('pyimeji')


class NoDefault(object):
    pass

NO_DEFAULT = NoDefault()


class Config(RawConfigParser):
    def __init__(self, **kw):
        config_dir = kw.pop('config_dir', None) or APP_DIRS.user_config_dir
        RawConfigParser.__init__(self, kw)

        cfg_path = os.path.join(config_dir, 'config.ini')
        if os.path.exists(cfg_path):
            assert os.path.isfile(cfg_path)
            self.read(cfg_path)
        else:
            if not os.path.exists(config_dir):
                try:
                    os.mkdir(config_dir)
                except OSError:  # pragma: no cover
                    # this happens when run on travis-ci, by a system user.
                    pass
            if os.path.exists(config_dir):
                with open(cfg_path, 'w') as fp:
                    self.write(fp)
        level = self.get('logging', 'level', default=None)
        if level:
            logging.basicConfig(level=getattr(logging, level))

    def get(self, section, option, default=NO_DEFAULT):
        if default is not NO_DEFAULT:
            if not self.has_option(section, option):
                return default
        return RawConfigParser.get(self, section, option)
