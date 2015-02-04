import os

from unittest import TestCase


class Tests(TestCase):
    def test_jsonload(self):
        from pyimeji.util import jsonload

        self.assertEquals(
            jsonload(os.path.join(os.path.dirname(__file__), 'test.json'))['status'],
            'ok')
