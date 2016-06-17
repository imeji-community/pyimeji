import os
import json

from unittest import TestCase
from pyimeji.api import Imeji


class Tests(TestCase):
    def test_jsonload(self):
        from pyimeji.util import jsonload

        self.assertEquals(
            jsonload(os.path.join(os.path.dirname(__file__), 'test.json'))['status'],
            'ok')


    def test_jsondumps(self):
        from pyimeji.util import jsonload, jsondumps
        object_test= jsonload(os.path.join(os.path.dirname(__file__), 'test.json'))
        with open(os.path.join(os.path.dirname(__file__), 'test.json'), mode='rb') as file:
            object_read = file.read()
        self.assertEqual (jsondumps(object_test), object_read)

    def test_pkg_path(self):
        import pyimeji
        from pyimeji.util import pkg_path

        func_test = pkg_path('test.json' )
        path_test = os.path.join(os.path.dirname(pyimeji.__file__), 'test.json')
        self.assertEquals(func_test, path_test)
