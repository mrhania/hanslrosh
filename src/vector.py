# -*- coding: utf-8 -*-

import math
from random import random


class Vec2:

    @staticmethod
    def dot(a, b):
        return a.x * b.x + a.y * b.y

    @staticmethod
    def angle(a, b):
        return math.degrees(math.atan2(b.y, b.x) - math.atan2(a.y, a.x))

    @staticmethod
    def random():
        return Vec2((random() * 2.0 - 1.0, random() * 2.0 - 1.0))

    def __init__(self, (x, y)):
        self.x = x
        self.y = y

    def __neg__(self):
        return Vec2((-self.x, -self.y))

    def __add__(self, v):
        return Vec2((self.x + v.x, self.y + v.y))

    def __sub__(self, v):
        return Vec2((self.x - v.x, self.y - v.y))

    def __rmul__(self, k):
        return Vec2((self.x * k, self.y * k))

    def __mul__(self, k):
        return Vec2((self.x * k, self.y * k))

    def __div__(self, k):
        return Vec2((self.x / k, self.y / k))

    def __str__(self):
        return "[" + str(self.x) + "; " + str(self.y) + "]"

    def tuplify(self):
        return (self.x, self.y)

    def length(self):
        return math.hypot(self.x, self.y)

    def unit(self):
        d = math.hypot(self.x, self.y)
        if d == 0.0:
            return Vec2((0.0, 0.0))
        return Vec2((self.x / d, self.y / d))

    def rotate(self, angle):
        x = math.cos(angle) * self.x - math.sin(angle) * self.y
        y = math.sin(angle) * self.x + math.cos(angle) * self.y

        return Vec2((x, y))

    def copy(self):
        return Vec2((self.x, self.y))
