import unittest

from jarn.mkrelease.lazy import lazy


class LazyTests(unittest.TestCase):

    def test_evaluate(self):
        called = []

        class Foo(object):
            @lazy
            def foo(self):
                called.append('foo')
                return 1

        f = Foo()
        self.assertEqual(f.foo, 1)
        self.assertEqual(len(called), 1)

    def test_evaluate_once(self):
        called = []

        class Foo(object):
            @lazy
            def foo(self):
                called.append('foo')
                return 1

        f = Foo()
        self.assertEqual(f.foo, 1)
        self.assertEqual(f.foo, 1)
        self.assertEqual(f.foo, 1)
        self.assertEqual(len(called), 1)

    def test_introspection(self):

        class Foo(object):
            def foo(self):
                """foo doc"""
            @lazy
            def lazy_foo(self):
                """lazy foo doc"""

        self.assertEqual(Foo.foo.__name__, "foo")
        self.assertEqual(Foo.foo.__doc__, "foo doc")
        self.assertEqual(Foo.lazy_foo.__name__, "lazy_foo")
        self.assertEqual(Foo.lazy_foo.__doc__, "lazy foo doc")

