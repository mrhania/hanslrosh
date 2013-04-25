# -*- coding: utf-8 -*-
import pygame
import camera
import tile
from tile import SIZE
from vector import Vec2
from utils import matrix

# obrazki do półcienia
PENUMBRA = {}
PENUMBRA[(-1, 0)] = pygame.image.load("gfx/tiles/gradh.png")
PENUMBRA[(+1, 0)] = pygame.transform.flip(PENUMBRA[(-1, 0)], True, False)
PENUMBRA[(0, -1)] = pygame.image.load("gfx/tiles/gradv.png")
PENUMBRA[(0, +1)] = pygame.transform.flip(PENUMBRA[(0, -1)], False, True)
# obrazki do pseudocienia
ANTUMBRA = {}
ANTUMBRA[(-1, -1)] = pygame.image.load("gfx/tiles/grado.png")
ANTUMBRA[(+1, -1)] = pygame.transform.flip(ANTUMBRA[(-1, -1)], True, False)
ANTUMBRA[(-1, +1)] = pygame.transform.flip(ANTUMBRA[(-1, -1)], False, True)
ANTUMBRA[(+1, +1)] = pygame.transform.flip(ANTUMBRA[(-1, -1)], True, True)

mult = ((+1, 0, 0, +1), (0, +1, +1, 0), (0, -1, +1, 0), (-1, 0, 0, +1),
        (-1, 0, 0, -1), (0, -1, -1, 0), (0, +1, -1, 0), (+1, 0, 0, -1))

# mapa kafli
width = 0
height = 0
tiles = None
# pozycja i zasięg światła
center = None
radius = None
# bitmapa z zapalonymi kawałkami
lightmap = None
# wyrenderowany zasięg widzenia
rendered = None
updated = False


def init(itiles, icenter, iradius):
    global width, height, tiles
    global center, radius
    global rendered

    width = len(itiles)
    height = len(itiles[0])
    tiles = itiles

    center = None
    radius = None

    update(icenter, iradius)


def update((x, y), r):
    global center, radius
    global lightmap, updated
    # jak centrum jest to co było to wszystko po staremu
    if center == (x, y) and radius == r:
        updated = False
        return
    # zaktualizuj to w takim razie
    center = (x, y)
    radius = r
    updated = True
    # a jak nie to lecimy z rzucaniem cienia
    lightmap = matrix((width, height), lambda: False)
    _enlight(x, y)
    for o in mult:
        _cast(x, y, 1, 1.0, 0.0, o[0], o[1], o[2], o[3])


def draw(surface):
    lbound = max(0, int(round(camera.pos.x / tile.SIZE)) - 1)
    rbound = min(width, int(round((camera.pos.x + camera.width) / tile.SIZE)) + 1)
    tbound = max(0, int(round(camera.pos.y / tile.SIZE)) - 1)
    bbound = min(height, int(round((camera.pos.y + camera.height) / tile.SIZE)) + 1)
    for x in range(lbound, rbound):
        for y in range(tbound, bbound):
            onscreen = camera.screen(Vec2((x, y)) * SIZE)
            # jak kafel nie jest zaświecony to przykro
            if not lightmap[x][y]:
                rect = pygame.Rect(onscreen, (SIZE + 1, SIZE + 1))
                surface.fill((0, 0, 0), rect)
                continue
            # nie ma sąsiadów, nie ma co sprawdzać
            if not (0 < x < width - 1 and 0 < y < height - 1):
                continue
            # jak jest zaświecony i ma koleżkę to rób półcień
            for ((dx, dy), image) in PENUMBRA.items():
                if not lightmap[x + dx][y + dy]:
                    surface.blit(image, onscreen)
            # jak jest zaświecony i ma tylko ukośnego kolegę to rób pseudocień
            for ((dx, dy), image) in ANTUMBRA.items():
                if not lightmap[x + dx][y + dy] and lightmap[x + dx][y] and lightmap[x][y + dy]:
                    surface.blit(image, onscreen)


def _cast(x, y, depth, start, end, xx, xy, yx, yy):
    # przedział do rzucania światła jest pusty, nie ma nic do roboty
    if start < end:
        return
    # iteracja po każdej współrzędnej w kolumnie
    for i in range(depth, radius + 1):
        # aktualnie rozpatrywane współrzędne
        (dx, dy) = (-i - 1, -i)
        # flaga informuje jaki rodzaj fragmentu jest przeszukiwany
        blocked = False
        # iteracja po każdej współrzędnej w wierszu
        while dx <= 0:
            dx += 1
            # współrzędne na mapie
            (mx, my) = (x + dx * xx + dy * xy, y + dx * yx + dy * yy)
            # nachylenie z lewej i z prawej strony rozpatrywanej pozycji
            lslope = (dx - 0.5) / (dy + 0.5)
            rslope = (dx + 0.5) / (dy - 0.5)
            # sprawdź czy nachylenie nie wychodzi poza przedział światła
            if start < rslope:
                continue
            if end > lslope:
                break
            # kafel się mieści, rozświetl go
            if dx * dx + dy * dy < radius * radius:
                _enlight(mx, my)
            if blocked:
                if _blocked(mx, my):
                    # przesuń kierunek rozświetlania
                    newstart = rslope
                    continue
                else:
                    # zakończ blokujący fragmentu
                    blocked = False
                    start = newstart
            else:
                if _blocked(mx, my) and i < radius:
                    # rozpocznij nowy blokujący fragment
                    blocked = True
                    # rzuć nowe światło na zaznaczonym przedziale
                    _cast(x, y, i + 1, start, lslope, xx, xy, yx, yy)
                    newstart = rslope
        # jeżeli mamy fragment blokujący to nawet nie ma co dalej iść
        if blocked:
            break


def _enlight(x, y):
    # zapal światło tylko pod warunkiem, że mieści się na planszy
    if 0 <= x < width and 0 <= y < height:
        lightmap[x][y] = True


def _blocked(x, y):
    # przypadek poza mapą
    if x < 0 or y < 0:
        return True
    if x >= width or y >= height:
        return True
    # przypadek normalny
    return tiles[x][y] == tile.WALL
