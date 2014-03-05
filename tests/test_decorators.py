import unittest
import mycroft


class TestOnDecorator(unittest.TestCase):

    def test_function_noargs(self):
        @mycroft.on('event1', 'event2')
        def func_thing():
            return 3
        self.assertEqual(
            3,
            func_thing()
        )
        self.assertEqual(
            ('event1', 'event2'),
            func_thing._mycroft_events
        )

    def test_function_args(self):
        @mycroft.on('event1')
        def func_thing(foo):
            return foo
        self.assertEqual(
            5,
            func_thing(5)
        )
        self.assertEqual(
            ('event1',),
            func_thing._mycroft_events
        )

    def test_class_method(self):
        class Inner:
            @mycroft.on('event1')
            def foo(self, bar):
                return bar
        inst = Inner()
        self.assertEqual(
            10,
            inst.foo(10)
        )
        self.assertEqual(
            ('event1',),
            Inner.foo._mycroft_events
        )
