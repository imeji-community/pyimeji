from __future__ import unicode_literals
from unittest import TestCase


class CliTest(TestCase):
    def test_parsed_kw(self):
        from pyimeji.cli import parsed_kw

        parsed = parsed_kw('a=2;b=3')
        self.assertEquals(parsed['a'], '2')

    def test_checked_call(self):
        from pyimeji.cli import checked_call

        def f1(a, b=3):
            return a + b

        def f2(exc=AssertionError):
            raise exc()

        self.assertEquals(checked_call(f1, 3), 6)
        self.assertIsInstance(checked_call(f2), Exception)
        self.assertRaises(ValueError, checked_call, f2, ValueError)
