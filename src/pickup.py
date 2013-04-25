# -*- coding: utf-8 -*-
"""Moduł z rzeczami, które się zbiera (jak pudełka)."""

import pygame
import random
import creature
import tile
import hud
import level
from entity import Entity


class Box(Entity):
    """Abstrakcyjna klasa dla pudełek."""
    IMAGE = None
    RADIUS = tile.SIZE

    def __init__(self, position, content=None):
        super(Box, self).__init__()
        self.position = position

    def append(self):
        raise NotImplemented("Box::append")

    def update(self, delta):
        super(Box, self).update(delta)
        # sprawdź czy gracz przypadkiem w skrzynkę nie wdepnął
        line = creature.Player().position - self.position
        if line.length() <= self.RADIUS:
            self.append()
            self.kill()


class MedBox(Box):
    """Pudełko z medykamentami, wiadomo - dodaje życie."""
    IMAGE = pygame.image.load("gfx/objects/medbox.png")

    def __init__(self, position, content=None):
        super(MedBox, self).__init__(position, content)
        # wylosuj ile ma przywracać punktów życia
        self.content = random.randint(5, 50)

    def append(self):
        # uzdrów gracza
        player = creature.Player()
        player.hitpoints = min(100.0, player.hitpoints + self.content)
        # wybierz tekst do wyświetlenia
        if self.content <= 10:
            hud.log("some drugs, nothing more")
        elif self.content <= 30:
            hud.log("yay, painkillers")
        else:
            hud.log("you should feel a lot better now")


class AmmoBox(Box):
    """Pudełko z nabojami."""
    IMAGE = pygame.image.load("gfx/objects/box.png")

    def __init__(self, position, content=None):
        super(AmmoBox, self).__init__(position, content)

        # jeżeli zostało sprecyzowane co ma być to fajnie
        if content:
            self.content = content
        else:
            # a jak nie to wygeneruj zawartość losowo
            if random.randint(0, 1) == 1:
                ammoak47 = random.randint(0, 100)
            else:
                ammoak47 = 0
            if random.randint(0, 1) == 1:
                ammoshotgun = random.randint(0, 10)
            else:
                ammoshotgun = 0
            self.content = {
                "ak47": ammoak47,
                "shotgun": ammoshotgun
            }

    def append(self):
        # dodaj graczowi naboje
        for (key, value) in self.content.items():
            # pomiń wartości zerowe
            if value <= 0:
                continue
            hud.log("you have found %s ammo for %s" % (value, key))
        for (name, value) in self.content.items():
            creature.Player().ammo[name] += value


class FoodBox(Box):
    """Kolejna klasa abstrakcyjna (wyspecyfikowane paczki mają obrazek)."""

    def __init__(self, position, content=None):
        super(FoodBox, self).__init__(position, content)
        # ilość żarła
        self.content = random.randint(10, 80)

    def append(self):
        player = creature.Player()
        player.hunger = max(0, player.hunger - self.content)

        if self.content <= 20:
            hud.log("scraps, ugh")
        elif self.content <= 50:
            hud.log("not much, but at least something to eat")
        elif self.content <= 75:
            hud.log("that looks very tasty")
        else:
            hud.log("it's delicious")


class FoodBox1(FoodBox):
    IMAGE = pygame.image.load("gfx/objects/foodbox_1.png")


class FoodBox2(FoodBox):
    IMAGE = pygame.image.load("gfx/objects/foodbox_2.png")


class FoodBox3(FoodBox):
    IMAGE = pygame.image.load("gfx/objects/foodbox_3.png")


class Hole(Box):
    """Dziura - jak gracz wdepnie to idzie poziom w dół."""
    # to głupie, że dziura dziedziczy po pudełku ale tak ma być
    IMAGE = pygame.image.load("gfx/objects/hole.png")
    RADIUS = 24

    def append(self):
        # dodaj graczowi punkty oczywiście
        creature.Player().points += (10 * level.storey) ** 2
        # gracz wdepnął w dziurę? ojej, idziemy w dół!
        level.create()
