import os

from unittest import TestCase


class Tests(TestCase):
    def test_pkg_path(self):
        import pyimeji
        from pyimeji.util import pkg_path

        func_test = pkg_path('test.json')
        path_test = os.path.join(os.path.dirname(pyimeji.__file__), 'test.json')
        self.assertEquals(func_test, path_test)

    def test_jsonload(self):
        from pyimeji.util import jsonload

        self.assertEquals(
            jsonload(os.path.join(os.path.dirname(__file__), 'test.json'))['status'],
            'ok')

    def test_jsondumps(self):
        from pyimeji.util import jsonload, jsondumps
        object_test = jsonload(os.path.join(os.path.dirname(__file__), 'test.json'))
        self.assertIsNotNone(jsondumps(object_test))
        self.assertEqual(jsondumps(object_test),
                         open(os.path.join(os.path.dirname(__file__), 'test.json'), mode='rb').read())
