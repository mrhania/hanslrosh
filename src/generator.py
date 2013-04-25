# -*- coding: utf-8 -*-
import tile
import weapon
import creature
from vector import Vec2
from random import random
from random import randint
from random import choice
from random import shuffle
from Queue import Queue

MAX_ROOMS = 1000
INTERSPACE = 4


def tiles(width, height):
    # tablica kwadratowa kafli
    tiles = [[tile.NULL for _ in range(height)] for _ in range(width)]
    doors = []

    def room(roomid=None):

        rwidth = randint(5, 10) * 2 + 1
        rheight = randint(5, 10) * 2 + 1
        posx = randint(INTERSPACE, width - rwidth - INTERSPACE)
        posy = randint(INTERSPACE, height - rheight - INTERSPACE)

        # sprawdź czy kafelki nie są zajęte
        for x in range(posx - INTERSPACE, posx + rwidth + INTERSPACE):
            for y in range(posy - INTERSPACE, posy + rheight + INTERSPACE):
                # jeżeli któryś kafel jest zajęty zwróć porażkę
                if tiles[x][y] != tile.NULL:
                    return False

        # jeżeli można umiejscowić pokój to spoko

        # ustaw ściany
        for x in range(posx, posx + rwidth + 1):
            tiles[x][posy] = tile.WALL
            tiles[x][posy + rheight] = tile.WALL
        for y in range(posy, posy + rheight + 1):
            tiles[posx][y] = tile.WALL
            tiles[posx + rwidth][y] = tile.WALL

        # ustaw podłoże
        for x in range(posx + 1, posx + rwidth):
            for y in range(posy + 1, posy + rheight):
                tiles[x][y] = tile.GROUND

        # generowanie drzwi
        count = choice([1, 1, 2, 2, 2, 2, 3, 3, 4])
        walltypes = ["n", "s", "w", "e"]
        shuffle(walltypes)

        for i in range(count):
            doorx = randint(posx + 1, posx + rwidth - 1)
            doory = randint(posy + 1, posy + rheight - 1)

            # drzwi na ścianie północnej
            if walltypes[i] == "n":
                doory = posy
            # drzwi na ścianie południowej
            if walltypes[i] == "s":
                doory = posy + rheight
            # drzwi na ścianie zachodniej
            if walltypes[i] == "w":
                doorx = posx
            # drzwi na ścianie wschodniej
            if walltypes[i] == "e":
                doorx = posx + rwidth

            tiles[doorx][doory] = tile.DOOR
            doors.append((roomid, doorx, doory))

    def passages():

        connected = [[False for _ in range(width)] for _ in range(height)]

        roomids = [[None for _ in range(width)] for _ in range(height)]
        for (roomid, doorx, doory) in doors:
            roomids[doorx][doory] = roomid

        # dla każdych drzwi znajdź jakieś drugie (utwórz połączenie)
        for (roomid, doorx, doory) in doors:

            # jak już są połączone to pozdro, nie ma sensu
            if connected[doorx][doory]:
                continue

            visited = [[False for _ in range(width)] for _ in range(height)]
            queue = Queue()

            visited[doorx][doory] = None
            queue.put((doorx, doory))
            # drzwi do których będę podłączał
            dest = None
            # pętla BFS
            while not queue.empty():
                (x, y) = queue.get()

                # dotarłem do jakichś niepołączonych drzwi
                if (
                    tiles[x][y] == tile.DOOR and
                    not connected[x][y] and
                    roomids[x][y] != roomid
                   ):
                    connected[doorx][doory] = True
                    connected[x][y] = True
                    dest = (x, y)
                    break

                # jak nie stoisz ani na drzwiach ani na niczym to walić to
                if (
                    tiles[x][y] != tile.NULL and
                    tiles[x][y] != tile.DOOR
                   ):
                    continue

                if not (x > 1 and
                        y > 1 and
                        x < width - 1 and
                        y < height - 1):
                    continue

                # odwiedź sąsiadów
                if (
                    (
                     tiles[x - 1][y] == tile.DOOR or
                     tiles[x][y] == tile.DOOR or
                     (
                      tiles[x][y - 1] == tile.NULL and
                      tiles[x][y + 1] == tile.NULL and
                      tiles[x - 1][y - 1] == tile.NULL and
                      tiles[x - 1][y + 1] == tile.NULL
                     )
                    ) and
                    not visited[x - 1][y]
                   ):
                    queue.put((x - 1, y))
                    visited[x - 1][y] = (x, y)

                if (
                    (
                     tiles[x][y - 1] == tile.DOOR or
                     tiles[x][y] == tile.DOOR or
                     (
                      tiles[x - 1][y] == tile.NULL and
                      tiles[x + 1][y] == tile.NULL and
                      tiles[x - 1][y - 1] == tile.NULL and
                      tiles[x + 1][y - 1] == tile.NULL
                     )
                    ) and
                    not visited[x][y - 1]
                   ):
                    queue.put((x, y - 1))
                    visited[x][y - 1] = (x, y)

                if (
                    (
                     tiles[x + 1][y] == tile.DOOR or
                     tiles[x][y] == tile.DOOR or
                     (
                      tiles[x][y - 1] == tile.NULL and
                      tiles[x][y + 1] == tile.NULL and
                      tiles[x + 1][y - 1] == tile.NULL and
                      tiles[x + 1][y + 1] == tile.NULL
                     )
                    ) and
                    not visited[x + 1][y]
                   ):
                    queue.put((x + 1, y))
                    visited[x + 1][y] = (x, y)

                if (
                    (
                     tiles[x][y + 1] == tile.DOOR or
                     tiles[x][y] == tile.DOOR or
                     (
                      tiles[x - 1][y] == tile.NULL and
                      tiles[x + 1][y] == tile.NULL and
                      tiles[x - 1][y + 1] == tile.NULL and
                      tiles[x + 1][y + 1] == tile.NULL
                     )
                    ) and
                    not visited[x][y + 1]
                   ):
                    queue.put((x, y + 1))
                    visited[x][y + 1] = (x, y)
            # jak nie znalazłeś żadnych drzwi to przykro
            if not dest:
                continue
            # ale jak coś jest to odtwórz ścieżkę
            (x, y) = dest
            (x, y) = visited[x][y]
            while not (x == doorx and y == doory):
                tiles[x][y] = tile.PASSAGE
                (x, y) = visited[x][y]

    # wygeneruj pokoje
    for roomid in range(MAX_ROOMS):
        room(roomid)

    # wygeneruj przejścia
    passages()

    return tiles


def items(tiles):
    """Generuje listę przedmiotów znajdujących się na mapie."""
    items = []
    for _ in range(100):
        case = randint(0, 2)
        pos = Vec2(position(tiles)) * tile.SIZE
        pos += Vec2((tile.SIZE / 2, tile.SIZE / 2))
        if case == 0:
            item = weapon.AK47()
            item.position = pos
        elif case == 1:
            item = weapon.Shotgun()
            item.position = pos
        elif case == 2:
            item = weapon.AmmoBox(pos)
        items.append(item)

    return items


def enemies(tiles, storey, limit=None):
    """Stawia na każdym możliwym polu jakiegoś kolesia."""
    # wynik działania funkcji (lista rozstawionych przeciwników)
    enemies = list()
    mid = Vec2((tile.SIZE, tile.SIZE)) * 0.5
    for x in range(len(tiles)):
        for y in range(len(tiles[0])):
            if tiles[x][y] == tile.GROUND:
                pos = Vec2((x, y)) * tile.SIZE + mid
                enemy = None
                # szasna na silnego przeciwnika
                if storey == 1:
                    strong = 0.0
                elif storey == 2:
                    strong = 2.5
                else:
                    strong = 5.0 * (storey - 2)
                # wylosuj rodzaj przeciwnika
                if strong > random() * 100.0:
                    case = randint(1, 2)
                else:
                    case = 0
                # stwórz przeciwnika wybranego rodzaju
                if case == 1:
                    enemy = creature.GlowingZombie(pos)
                elif case == 2:
                    enemy = creature.Skeleton(pos)
                else:
                    enemy = creature.Zombie(pos)
                # dodaj gościa do listy przeciwników
                enemies.append(enemy)
    # przetasuj, żeby byli losow rozstawieni
    shuffle(enemies)
    if limit:
        return enemies[:limit]
    else:
        return enemies


def position(tiles, spec=None):
    """Generuje losową pozycję na mapie (do umiejscawiania obiektów)."""
    width = len(tiles)
    height = len(tiles[0])

    # oblicz przedziały
    if spec:
        (x, y, radius) = spec
        boundl = max(1, x - radius)
        boundr = min(width - 1, x + radius)
        boundt = max(1, y - radius)
        boundb = min(height - 1, y + radius)
    else:
        boundl = 1
        boundr = width - 1
        boundt = 1
        boundb = height - 1

    # losuj pozycje w zadanym przedziale aż nie trafisz w dobrą
    fine = [tile.GROUND, tile.PASSAGE, tile.DOOR]
    while True:
        sx = randint(boundl, boundr)
        sy = randint(boundt, boundb)
        if tiles[sx][sy] in fine:
            break

    return (sx, sy)
