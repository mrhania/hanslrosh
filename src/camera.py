# -*- coding: utf-8 -*-

from vector import Vec2

width = 640
height = 480
speed = 0.1

pos = Vec2((0, 0))


def lookat(entity):
    global pos
    pos = entity.position - Vec2((width / 2, height / 2))


def screen(vec):
    return (vec - pos).tuplify()


def real(vec):
    return (vec + pos).tuplify()
