# -*- coding: utf-8 -*-

import generator
import tile
import camera
import weapon
import fov
import pickup
import menu
from random import randint
from random import shuffle
from random import choice
from pygame import Rect
from utils import matrix
from entity import Manager
from vector import Vec2
from tile import *
from creature import *

# o ile ma wzrastać liczba przeciwników po zejściu na niższe piętro
ZOMBIES_COUNT = 50
# obazek z ekranem ładowania
loadingscreen = pygame.image.load("gfx/loading.png")

_screen = None
# mapa, składa się z kafli
tiles = None
tilemap = None
# lista przeciwników
creaturesqueued = None
creatures = None
# lista przedmiotów
items = None
# parametry poziomu
storey = 0
width = None
height = None


def init(screen, iwidth, iheight, istorey=0):
    global tiles, tilemap
    global creatures, creaturesqueued
    global items
    global width, height
    global _screen
    global storey
    width = iwidth
    height = iheight

    storey = 0
    _screen = screen
    # broń podstawowa, dostępna na starcie
    gun = weapon.Deagle(Player())
    Player().weapon = gun


def create(stor=None):
    global storey
    global tiles, tilemap
    global creatures, creaturesqueued
    global items
    # nabazgraj ekran ładowania
    _screen.blit(loadingscreen, (0, 0))
    pygame.display.update()
    # zwiększ poziom
    if not stor:
        storey += 1
    else:
        storey = 1
    # lista przedmiotów
    items = Manager((tile.SIZE, tile.SIZE), (width, height))
    creatures = Manager((tile.SIZE, tile.SIZE), (width, height))
    # wygeneruj nową mapę
    tiles = _generate(width, height)
    # gracz
    Player().position = Vec2(generator.position(tiles)) * tile.SIZE
    Player().weapon.position = Player().position
    # daj graczu 5 sekund nieśmiertelności na przygotowanie
    Player().immunetime = 5000
    creatures.add(Player())
    items.add(Player().weapon)
    camera.lookat(Player())
    # wygeneruj listę przeciwników
    creaturesqueued = generator.enemies(tiles, storey)
    for _ in xrange(ZOMBIES_COUNT * storey):
        creatures.add(creaturesqueued[-1])
        creaturesqueued.pop()
    # zainicjalizuj zasięg widzenia
    fov.init(tiles, tile.on(Player().position), 7)


def update(delta):
    # aktualizacja wszystkich przedmitów
    items.update(delta)
    # aktualizacja wszystkich żywych cośów w grze
    creatures.update(delta)
    # aktualizacja zasięgu widzenia
    pos = Player().position / 32.0
    fov.update((int(round(pos.x - 0.5)), int(round(pos.y - 0.5))), 7)
    # sprawdź stan gracza - jak nie żyje to przejdź do ekranu wyników
    if Player().hitpoints <= 0.0:
        menu.inputtext = ""
        menu.kind = "end"


def draw(surface):
    # narysuj mapę
    surface.blit(tilemap, camera.screen(Vec2((0, 0))))
    # rysowanie przedmiotów
    items.draw(surface)
    # rysowanie przeciwników
    creatures.draw(surface)


def _minimap(surface):
    surface.lock()
    for x in range(len(tiles)):
        for y in range(len(tiles[0])):
            if tiles[x][y] == GROUND:
                surface.set_at((x, y), (255, 255, 255))
    surface.unlock()


def _generate(width, height):
    """Generuje nową planszę"""
    # plansza kafli
    tiles = matrix((width, height), lambda: " ")
    # prerenderowana mapa
    global tilemap
    tilemap = pygame.Surface(((width + 1) * SIZE, (height + 1) * SIZE))
    for x in range(width + 1):
        for y in range(height + 1):
            rect = choice(GROUND_RECTS)
            position = rect.copy()
            position.bottomright = ((x + 1) * SIZE, (y + 1) * SIZE)
            tilemap.blit(GROUND_ATLAS, position, rect)

    def lab(rect):
        """Generuje labolatorium na zadanym prostokącie."""
        # sprawdź czy miejsce nie jest czasem za małe na labolatorium
        if rect.height < 7 or rect.width < 7:
            return False
        # zrób "posadzkę"
        for x in range(rect.left + 1, rect.right):
            for y in range(rect.top + 1, rect.bottom):
                tilemap.blit(choice(LAB_IMAGES), (x * SIZE, y * SIZE))
        # udało się wygenerować, sukces
        return True

    def holeroom(rect):
        """Generuje eee... "pokój z dziurą"..."""
        # pokoje z dziurą są bardzo małych rozmiarów
        if not (1 <= rect.height <= 4 and 1 <= rect.width <= 4):
            return False
        # jak wymiary się zgadzają to tylko w 33% przypadków robimy dziurę
        if not (random.randint(1, 100) in range(1, 34)):
            return False
        # weź środek pokoju i ustaw tam dziurę
        pos = Vec2(rect.center) * tile.SIZE
        pos += Vec2((tile.SIZE / 2, tile.SIZE / 2))
        items.add(pickup.Hole(pos))
        # łii, mamy dziurawy pokój
        return True

    def magazine(rect):
        """Generuje magazyn na zadanym prostokącie."""
        # magazyn musi mieć małe rozmiary
        if not (1 <= rect.height <= 5 and 1 <= rect.width <= 5):
            return False
        # wygeneruj pudła i bronie
        for x in range(rect.left + 1, rect.right):
            for y in range(rect.top + 1, rect.bottom):
                case = randint(0, 100)
                pos = Vec2((x, y)) * tile.SIZE
                pos += Vec2((tile.SIZE / 2, tile.SIZE / 2))
                item = None
                if 0 <= case < 25:
                    item = pickup.AmmoBox(pos)
                elif 25 <= case < 30:
                    item = pickup.MedBox(pos)
                elif 30 <= case < 35:
                    item = weapon.AK47()
                    item.position = pos
                elif 35 <= case < 40:
                    item = weapon.Shotgun()
                    item.position = pos
                elif 40 <= case < 45:
                    item = weapon.AWP()
                    item.position = pos
                elif 45 <= case < 50:
                    item = weapon.Deagle()
                    item.position = pos
                elif 50 <= case < 54:
                    item = pickup.FoodBox1(pos)
                elif 54 <= case < 58:
                    item = pickup.FoodBox2(pos)
                elif 58 <= case < 62:
                    item = pickup.FoodBox3(pos)
                if item:
                    items.add(item)
        # udało się wygenerować, sukces
        return True

    def bsp(rect):
        """Tworzy podkomory poprzez podział przestrzeni."""
        MIN = 4
        # pokój jest wystarczająco mały aby go zapełnić
        if rect.width <= 2 * MIN and rect.height <= 2 * MIN:
            # ustaw ściany na obwodzie
            for x in range(rect.left, rect.right + 1):
                tiles[x][rect.top] = tiles[x][rect.bottom] = "#"
            for y in range(rect.top, rect.bottom + 1):
                tiles[rect.left][y] = tiles[rect.right][y] = "#"
            # spróbuj wygenerować pokoje
            if lab(rect):
                return
            if holeroom(rect):
                return
            if magazine(rect):
                return
            return
        # podziel i rekurencyjnie wygeneruj podpokoje
        direction = randint(0, 1)
        if rect.width <= 2 * MIN:
            direction = 1
        if rect.height <= 2 * MIN:
            direction = 0
        if direction == 0:
            # podziel w poziomie
            #widthl = MIN + randint(0, max(0, min(MAX, rect.width - 2 * MIN)))
            widthl = rect.width / 2 - randint(-MIN / 2, +MIN / 2)
            widthr = rect.width - widthl
            # generowanie dla lewej części
            rectl = Rect(rect.left, rect.top, widthl, rect.height)
            bsp(rectl)
            # generowanie dla prawej części
            rectr = Rect(rectl.right, rect.top, widthr, rect.height)
            bsp(rectr)
            # wybierz punkt będący przejściem z jednej do drugiej komnaty
            ys = list(range(rect.top + 1, rect.bottom - 1))
            shuffle(ys)
            dx = rectl.right
            for dy in ys:
                if tiles[dx - 1][dy] == " " and tiles[dx + 1][dy] == " ":
                    tiles[dx][dy] = "X"
                    position = (dx * SIZE, dy * SIZE - SIZE / 2)
                    tilemap.blit(choice(DOORV_IMAGES), position)
                    return
        else:
            # podziel w pionie
            #heightt = MIN + randint(0, max(0, min(MAX, rect.height - 2 * MIN)))
            heightt = rect.height / 2 - randint(-MIN / 2, +MIN / 2)
            heightb = rect.height - heightt
            # generowanie górnej części
            rectt = Rect(rect.left, rect.top, rect.width, heightt)
            bsp(rectt)
            # generowanie dolnej części
            rectb = Rect(rect.left, rectt.bottom, rect.width, heightb)
            bsp(rectb)
            # wybierz punkt będący przejściem z jednej do drugiej komnaty
            xs = list(range(rect.left + 1, rect.right - 1))
            shuffle(xs)
            dy = rectt.bottom
            for dx in xs:
                if tiles[dx][dy - 1] == " " and tiles[dx][dy + 1] == " ":
                    tiles[dx][dy] = "X"
                    position = (dx * SIZE - SIZE / 2, dy * SIZE)
                    tilemap.blit(choice(DOORH_IMAGES), position)
                    return

    # generowanie mapy + częściowe rysowanie
    bsp(Rect(1, 1, width - 2, height - 2))
    # rysowanie ścian
    for x in range(1, width):
        for y in range(1, height):
            if tiles[x][y] == "#":
                # mamy do czynienia ze ścianą, określ w którą stronę
                if x > 0 and tiles[x - 1][y] == "#":
                    # ściana pozioma, lewa część
                    position = (x * SIZE, y * SIZE)
                    rect = Rect(0, 0, SIZE / 2, SIZE)
                    tilemap.blit(choice(WALLH_IMAGES), position, rect)
                if x < width - 1 and tiles[x + 1][y] == "#":
                    # ściana pozioma, prawa część
                    position = (x * SIZE + SIZE / 2, y * SIZE)
                    rect = Rect(SIZE / 2, 0, SIZE / 2, SIZE)
                    tilemap.blit(choice(WALLH_IMAGES), position, rect)
                if y > 0 and tiles[x][y - 1] == "#":
                    # ściana pionowa, górna część
                    position = (x * SIZE, y * SIZE)
                    rect = Rect(0, 0, SIZE, SIZE / 2)
                    tilemap.blit(choice(WALLV_IMAGES), position, rect)
                if y < height - 1 and tiles[x][y + 1] == "#":
                    # ściana pionowa, dolna część
                    position = (x * SIZE, y * SIZE + SIZE / 2)
                    rect = Rect(0, SIZE / 2, SIZE, SIZE / 2)
                    tilemap.blit(choice(WALLV_IMAGES), position, rect)

    # deascyfikacja (piękne słówko: zamiana znaczków ASCII na wyliczenia)
    unasciify = lambda field: WALL if field == "#" else GROUND
    return map(lambda row: map(unasciify, row), tiles)
