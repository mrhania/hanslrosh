# -*- coding: utf-8 -*-
"""
Moduł to coś na wzór modułu `sprite` ze standardowego pygame, tyle że ten jest
zoptymalizowany konkretnie pod plansze oparte na kaflach. Dzięki temu kolizje
mogę sobie sprawdzać w czasie nieporównywalnie szybszym niż w wersji zwykłej,
czy też w oparci o jakieś wysublimowane drzewa czwórkowe. Podstawową klasą
jest `Entity` (opdowiednik standardowego `Sprite`) oraz `Manager` (odpowiednik
standardowego `Group`). I to w zasadzie tylko tyle mi chyba wystarczy.
"""
import camera
from utils import matrix
from vector import Vec2
from animation import Animation
import creature


class Entity(object):
    IMAGE = None
    RADIUS = 0

    def __init__(self):
        # klatki animacji, generowane na podstawie wspólnego obrazka
        self.image = Animation(self.IMAGE)
        # atrybuty jednostki (prędkość i rotacja nie muszą być ustawiane)
        self.position = Vec2((0.0, 0.0))
        self.velocity = Vec2((0.0, 0.0))
        self.rotation = None
        # dane dla menedżera
        self._mdelete = False

    def collide(self):
        return False

    def kill(self):
        self._mdelete = True

    def update(self, delta):
        # aktualizuj pozycję uważając na kolizje
        self.position.x += self.velocity.x * delta
        if self.collide():
            self.position.x -= self.velocity.x * delta
        self.position.y += self.velocity.y * delta
        if self.collide():
            self.position.y -= self.velocity.y * delta
        # aktualizacja animacji
        self.image.update(delta)

    def draw(self, surface):
        spos = camera.screen(self.position)
        self.image.draw(surface, spos, self.rotation)
        """
        spos = (int(spos[0]), int(spos[1]))
        pygame.draw.circle(surface, (255, 0, 0), spos, int(self.RADIUS), 1)
        """


class Manager(object):

    def __init__(self, chunksize, mapsize):
        # zapisz wymiary (tak dla jaj)
        self.chunksize = chunksize
        self.mapsize = mapsize
        # lista wszystkich obiektów (do szybkiego iterowania)
        self.items = set()
        # mapa o zadanych wymiarach (eo szybkich obliczeń)
        self.chunks = matrix(mapsize, lambda: set())

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def chunk(self, entity):
        """Oblicza, w którym kawałku znajduje się jednostka."""
        x = int(entity.position.x / self.chunksize[0])
        y = int(entity.position.y / self.chunksize[1])
        return (x, y)

    def collide(self, entity):
        """Sprawdza czy obiekt koliduje z którymś z obiektów w zasięgu."""

        def collideset(entity, chunk):
            """Sprawdza kolizję z określonym zbiorem."""
            for item in chunk:
                # jeżeli to jest ten sam obiekt to nie o to chodzi
                if entity == item:
                    continue
                # porównaj promienie
                dist = (entity.position - item.position).length()
                if dist <= entity.RADIUS + item.RADIUS:
                    return item
            # widocznie z niczym nie koliduje
            return None
        neighbours = list([
            (-1, -1), (0, -1), (+1, -1),
            (-1,  0), (0,  0), (+1,  0),
            (-1, +1), (0, +1), (+1, +1)
        ])
        # sprawdź kolizję z sąsiednimi kawałkami
        (x, y) = self.chunk(entity)
        for (nx, ny) in neighbours:
            # uważaj, żeby nie wyjechać za granicę mapy
            if not (0 <= x + nx < self.mapsize[0] and 0 <= y + ny < self.mapsize[1]):
                continue
            check = collideset(entity, self.chunks[x + nx][y + ny])
            if check:
                return check
        # czysto, z nikim nie ma kolizji
        return None

    def collideall(self, entity):
        """Sprawdza czy obiekt koliduje z wieloma obiektami w zasięgu."""

        def collideset(entity, chunk):
            """Sprawdza kolizję z określonym zbiorem."""
            result = list()
            for item in chunk:
                # jeżeli to jest ten sam obiekt to nie o to chodzi
                if entity == item:
                    continue
                # porównaj promienie
                dist = (entity.position - item.position).length()
                if dist <= entity.RADIUS + item.RADIUS:
                    result.append(item)
            # widocznie z niczym nie koliduje
            return result

        neighbours = list([
            (-1, -1), (0, -1), (+1, -1),
            (-1,  0), (0,  0), (+1,  0),
            (-1, +1), (0, +1), (+1, +1)
        ])
        # lista wszystkich trafionych obiektów
        result = list()
        # sprawdź kolizję z sąsiednimi kawałkami
        (x, y) = self.chunk(entity)
        for (nx, ny) in neighbours:
            # uważaj, żeby nie wyjechać za granicę mapy
            if not (0 <= x + nx < self.mapsize[0] and 0 <= y + ny < self.mapsize[1]):
                continue
            # dodaj kolidujących z określonego kawałka
            result += collideset(entity, self.chunks[x + nx][y + ny])
        return result

    def add(self, entity):
        """Dodaje nową jednostkę do menedżera."""
        self.items.add(entity)
        (x, y) = self.chunk(entity)
        self.chunks[x][y].add(entity)

    def remove(self, entity):
        """Usuwa istniejącą jednostkę z menedżera."""
        self.items.remove(entity)
        (x, y) = self.chunk(entity)
        self.chunks[x][y].remove(entity)

    def update(self, delta):
        """Aktualizuje wszystkie jednostki będące pod kontrolą menedżera."""
        # granice obszaru widzianego przez kamerę
        boundl = camera.pos.x - self.chunksize[0]
        boundr = camera.pos.x + camera.width + self.chunksize[0]
        boundt = camera.pos.y - self.chunksize[1]
        boundb = camera.pos.y + camera.height + self.chunksize[1]
        for item in self.items:
            # sprawdź czy aktualizowany obiekt mieści się na ekranie
            if item.position.x < boundl or item.position.x > boundr:
                continue
            if item.position.y < boundt or item.position.y > boundb:
                continue
            (ox, oy) = self.chunk(item)
            item.update(delta)
            (nx, ny) = self.chunk(item)
            # sprawdź czy obiekt nie przeszedł przypadkiem do innego kawałka
            if (ox, oy) != (nx, ny):
                self.chunks[ox][oy].remove(item)
                self.chunks[nx][ny].add(item)
            # sprawdź czy nie trzeba wywalić obiektu
            if item._mdelete:
                self.chunks[nx][ny].remove(item)
        # zostaw tylko te elementy, które faktycznie trzeba usunąć
        self.items = set(filter(lambda item: not item._mdelete, self.items))

    def draw(self, surface):
        """Rysuje wszystkie jednostki będące pod kontrolą menedżera."""
        # granice obszaru widzianego przez kamerę
        boundl = camera.pos.x - self.chunksize[0]
        boundr = camera.pos.x + camera.width + self.chunksize[0]
        boundt = camera.pos.y - self.chunksize[1]
        boundb = camera.pos.y + camera.height + self.chunksize[1]
        for item in self.items:
            # sprawdź czy rysowany obiekt mieści się na ekranie
            if item.position.x < boundl or item.position.x > boundr:
                continue
            if item.position.y < boundt or item.position.y > boundb:
                continue
            # jak się mieści to fajno, rysuj go
            item.draw(surface)
