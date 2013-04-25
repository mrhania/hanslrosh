# -*- coding: utf-8 -*-

import pygame

# zwyczajne kafle
NULL = 0
WALL = 1
GROUND = 2
PASSAGE = 3
DOOR = 4
BANG = 5

# kafle obrazkowe
SIZE = 32

GROUND_IMAGE = pygame.image.load("gfx/tiles/wood.png")
NULL_IMAGE = pygame.image.load("gfx/tiles/grass.png")
WALL_IMAGE = pygame.image.load("gfx/tiles/brick.png")
DOOR_IMAGE = pygame.image.load("gfx/tiles/pit.png")
PASSAGE_IMAGE = pygame.image.load("gfx/tiles/stone.png")

GROUND_ATLAS = pygame.image.load("gfx/tiles/ground_atlas.png")
GROUND_RECTS = [
    pygame.Rect(0, 0, 32, 32),
    pygame.Rect(32, 0, 32, 32),
    pygame.Rect(64, 0, 32, 32),
    pygame.Rect(96, 0, 32, 32),
    pygame.Rect(0, 32, 32, 64),
    pygame.Rect(32, 32, 32, 64),
    pygame.Rect(64, 32, 64, 32),
    pygame.Rect(64, 64, 64, 32)
]

LAB_IMAGES = [
    pygame.image.load("gfx/tiles/lab_1.png"),
    pygame.image.load("gfx/tiles/lab_2.png"),
    pygame.image.load("gfx/tiles/lab_3.png"),
    pygame.image.load("gfx/tiles/lab_4.png")
]

WALLV_IMAGES = [
    pygame.image.load("gfx/tiles/wall_1.png"),
    pygame.image.load("gfx/tiles/wall_2.png"),
    pygame.image.load("gfx/tiles/wall_3.png")
]
WALLH_IMAGES = map(lambda img: pygame.transform.rotate(img, 90), WALLV_IMAGES)

DOORV_IMAGES = [
    pygame.image.load("gfx/tiles/door_1.png")
]
DOORH_IMAGES = map(lambda img: pygame.transform.rotate(img, 90), DOORV_IMAGES)


def on(position):
    """Zamienia pozycję rzeczywistą na kafel."""
    return (int(position.x / SIZE), int(position.y / SIZE))


def get_image(tiles, (x, y)):
    if tiles[x][y] == GROUND:
        return GROUND_IMAGE
    if tiles[x][y] == PASSAGE:
        return PASSAGE_IMAGE
    if tiles[x][y] == WALL:
        return WALL_IMAGE
    if tiles[x][y] == DOOR:
        return DOOR_IMAGE
    if tiles[x][y] == NULL:
        return NULL_IMAGE
