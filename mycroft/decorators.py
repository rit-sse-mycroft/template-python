"""
decorators.py

This file contains decorators for Mycroft,
mainly used for storing meta information about event handling
"""


def on(verb):
    """
    A decorator for registering a function.
    Note: Python decorators that accept arguments need to return
          a decorator function, which in turn returns the actual
          function to use.
    Args:
        verb - str, what verb this function responds to
    """
    def inner(func):
        func._mycroft_event = verb
        return func
    return inner
