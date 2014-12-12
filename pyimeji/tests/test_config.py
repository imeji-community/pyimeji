from __future__ import unicode_literals
import os
from tempfile import mkdtemp
from unittest import TestCase
from shutil import rmtree
from io import open


class ConfigTest(TestCase):
    def setUp(self):
        self.tmp = mkdtemp()
        self.cfg = os.path.join(self.tmp, '.config')

    def tearDown(self):
        rmtree(self.tmp, ignore_errors=True)

    def test_new_config(self):
        from pyimeji.config import Config

        self.assertFalse(os.path.exists(self.cfg))
        Config(config_dir=self.cfg)
        self.assertTrue(os.path.exists(self.cfg))

    def test_existing_config(self):
        from pyimeji.config import Config

        os.mkdir(self.cfg)
        with open(os.path.join(self.cfg, 'config.ini'), 'w', encoding='utf8') as fp:
            fp.write("""\
[section]
option = 12
""")

        cfg = Config(config_dir=self.cfg)
        self.assertEqual(cfg.get('section', 'option'), '12')
