# -*- coding: utf-8 -*-
"""
Ten moduł służy do trzymania rzeczy, które nie zasłużyły by dostać własny.
"""


class Singleton(type):
    """Klasa do robienia z innych klas singletonów, fajna rzecz."""

    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


def matrix((width, height), generator=None):
    """Tworzy macierz o zadanych rozmiarach przy pomocy funkcji generującej."""
    if generator:
        return [[generator() for _ in xrange(height)] for _ in xrange(width)]
    else:
        return [[None for _ in xrange(height)] for _ in xrange(width)]
