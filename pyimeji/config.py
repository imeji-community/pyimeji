import os

from appdirs import AppDirs
from six.moves.configparser import RawConfigParser


APP_DIRS = AppDirs('pyimeji')


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
