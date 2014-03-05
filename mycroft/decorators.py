"""
decorators.py

This file contains decorators for Mycroft,
mainly used for storing meta information about event handling
"""


def on(*args):
    """
    A decorator for registering a function.
    Note: Python decorators that accept arguments need to return
          a decorator function, which in turn returns the actual
          function to use.
    Args:
        any number of strings you like, each being an event name
        example: `@mycroft.on('MSG_QUERY_SUCCESS', 'MSG_QUERY')`
    """
    def inner(func):
        func._mycroft_events = args
        return func
    return inner
