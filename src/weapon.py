# -*- coding: utf-8 -*-
"""
Moduł z broniami.
"""
import pygame
import camera
import tile
import level
import creature
import random
import hud
import particles
from vector import Vec2
from entity import Entity
from pygame.sprite import Sprite
from pygame import Rect


class AmmoBox(Entity):
    """Pudełko z nabojami."""
    IMAGE = pygame.image.load("gfx/objects/box.png")
    RADIUS = tile.SIZE / 2

    def __init__(self, position, content=None):
        super(AmmoBox, self).__init__()
        self.position = position

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

    def update(self, delta):
        super(AmmoBox, self).update(delta)
        # sprawdź czy gracz przypadkiem w skrzynkę nie wdepnął
        line = creature.Player().position - self.position
        if line.length() <= tile.SIZE:
            # dodaj mu naboje
            for (key, value) in self.content.items():
                # pomiń wartości zerowe
                if value <= 0:
                    continue
                hud.log("you have found %s ammo for %s" % (value, key))
            for (name, value) in self.content.items():
                creature.Player().ammo[name] += value
            # usuń się zewsząd
            self.kill()


class Bullet(object):
    """Klasa reprezentująca bardzo prosty pocisk."""
    RADIUS = 3
    POWER = 10
    LIFETIME = 1000

    def __init__(self, position, velocity, shooter=None):
        # wektory pozycji i prędkości
        self.position = position + 25.0 * velocity
        self.velocity = velocity
        self.lifetime = self.LIFETIME
        self.alive = True
        # dla przyjaznego ognia zapamiętaj kto wystrzelił
        self.shooter = shooter

    def update(self, delta):
        # przesuwańsko i takie tam
        self.lifetime -= delta
        if self.lifetime <= 0:
            self.alive = False
        self.position += self.velocity * delta
        # sprawdź czy pocisk nie pieprznął w ścianę
        tilex = int(self.position.x / tile.SIZE)
        tiley = int(self.position.y / tile.SIZE)
        if not (level.tiles[tilex][tiley] == tile.GROUND or
                level.tiles[tilex][tiley] == tile.PASSAGE or
                level.tiles[tilex][tiley] == tile.DOOR):
            self.alive = False
            # stwórz efekt cząsteczkowy pieprznięcia o mur
            for _ in range(5):
                velocity = self.velocity.rotate((random.random() - 0.5))
                particles.Puff(self.position.copy(), -velocity * 0.1)

        # jak nie żyjemy to heloł, co ty tutaj robisz?
        if not self.alive:
            return
        # weź wrzystkie biedaczyska, które zostaną trafione
        hitted = level.creatures.collideall(self)
        for creat in hitted:
            # nie zabijaj tego kto wystrzelił (przyjazny ogień)
            if creat == self.shooter:
                continue
            creat.hit(self.POWER)
            self.alive = False

    def draw(self, surface):
        rect = pygame.Rect(0, 0, 3, 3)
        rect.center = camera.screen(self.position)
        surface.fill((255, 255, 255), rect)


class Shotshell(Bullet):
    """Pociski do strzelby (łuska ze śrutem)."""
    LIFETIME = 10

    def update(self, delta):
        super(Shotshell, self).update(delta)
        # jak w nic nie walnęło z bliska to rozpaćkaj w powietrzu śrut
        if self.lifetime <= 0:
            # strzelba miota kilkoma pociskami z mniejszą dokładnością
            for _ in range(8):
                # weź trochę odchyl kąt lotu pocisku
                real = self.velocity.rotate((random.random() - 0.5) * 0.25)
                # trochę go spowolnij (albo przyśpiesz, dla hecy)
                real *= random.random() * 0.4 + 0.8
                shot = Bullet(self.position.copy(), real)
                self.shooter.weapon.projectiles.append(shot)


class Snipershot(Bullet):
    POWER = 100

    def __init__(self, position, velocity, shooter=None):
        super(Snipershot, self).__init__(position, velocity, shooter)
        self.velocity *= 1.5


class Projectile(Sprite):
    """Klasa reprezentująca "widzialny" pocisk."""

    def __init__(self, position, velocity):
        # wektory pozycji i prędkości
        self.position = position + 25.0 * velocity
        self.velocity = velocity
        # atrybuty
        self.power = 1
        self.lifetime = 1000
        # czy pocisk nadaje się do usunięcia?
        self.alive = True
        # obrazek pocisku
        self.image = None
        self.rect = Rect(0, 0, tile.SIZE, tile.SIZE)

    def update(self, delta):
        # sprawdź czy czas życia pocisku nie dobiegł końca
        self.lifetime -= delta
        if self.lifetime <= 0:
            self.alive = False
        # przesuń pozycję o wektor prędkości
        self.position += self.velocity * delta
        self.rect.center = (int(self.position.x), int(self.position.y))
        # zaktualizuj animację
        self.image.update(delta)

    def draw(self, surface):
        # pionowa oś
        ox = Vec2((camera.width / 2, 0)) - camera.center()
        # obróć obrazek względem pionowej osi
        rotation = Vec2.angle(self.velocity, ox)
        position = camera.screen(self.position)
        self.image.draw(surface, position, rotation)


class Weapon(Entity):
    NAME = None
    IMAGE = None
    IMAGE_GROUND = None
    COOLDOWN = 0
    RELOADTIME = 0
    MAGAZINE = None
    AMMO = Bullet

    def __init__(self, owner=None):
        super(Weapon, self).__init__()
        self.magazine = 0
        self.owner = owner
        self.projectiles = []
        self.cooldown = 0

    def reload(self):
        # weź tylko tyle ile trzeba i ile mieści się w magazynku
        taken = min(self.MAGAZINE - self.magazine, self.owner.ammo[self.NAME])
        self.magazine += taken
        self.owner.ammo[self.NAME] -= taken
        self.cooldown = self.RELOADTIME

    def trigger(self, dest):
        if self.cooldown <= 0:
            # jeżeli magazynek jest pusty rozpłacz się
            if self.magazine <= 0:
                return
            # oblicz wektor prędkości pocisku (na podstawie pozycji celu)
            position = self.position.copy()
            velocity = (dest - position).unit() * 0.5
            # wystrzel pocisk z magazynka i ustaw odstęp czasowy
            self.projectiles.append(self.AMMO(position, velocity, self.owner))
            self.magazine -= 1
            self.cooldown = self.COOLDOWN

    def update(self, delta):
        super(Weapon, self).update(delta)
        self.cooldown -= delta
        if self.owner:
            # jeżeli broń ma posiadacza to jej pozycja jest taka sama
            self.position = self.owner.position
            # aktualizacja animacji
            self.image.update(delta)
            # zaktualizuj każdy pocisk, który został wystrzelony
            for proj in self.projectiles:
                proj.update(delta)
            # zostaw tylko te pociski, które są "aktywne"
            self.projectiles = filter(lambda p: p.alive, self.projectiles)
        # a jak nie to ma swoją własną
        else:
            self.position = self.position.copy()

    def draw(self, surface):
        # jeżeli broń nie leży na podłodze to rysuj ją "przy właścicielu"
        if self.owner:
            # narysuj każdy wystrzelony pocisk
            for proj in self.projectiles:
                proj.draw(surface)
            # narysuj broń
            position = camera.screen(self.position)
            self.image.draw(surface, position, self.owner.rotation)
        else:
            # narysuj leżącą broń
            rect = self.IMAGE_GROUND.get_rect()
            rect.center = camera.screen(self.position)
            surface.blit(self.IMAGE_GROUND, rect)


class AK47(Weapon):
    NAME = "ak47"
    IMAGE = pygame.image.load("gfx/weapons/ak47.png")
    IMAGE_GROUND = pygame.image.load("gfx/weapons/ak47_g.png")
    MAGAZINE = 30
    COOLDOWN = 100
    RELOADTIME = 1000
    AMMO = Bullet


class Shotgun(Weapon):
    NAME = "shotgun"
    IMAGE = pygame.image.load("gfx/weapons/shotgun.png")
    IMAGE_GROUND = pygame.image.load("gfx/weapons/shotgun_g.png")
    MAGAZINE = 8
    COOLDOWN = 500
    RELOADTIME = 3000
    AMMO = Shotshell


class AWP(Weapon):
    NAME = "awp"
    IMAGE = pygame.image.load("gfx/weapons/awp.png")
    IMAGE_GROUND = pygame.image.load("gfx/weapons/awp_g.png")
    MAGAZINE = 3
    COOLDOWN = 1000
    RELOADTIME = 3000
    AMMO = Snipershot


class Deagle(Weapon):
    NAME = "deagle"
    IMAGE = pygame.image.load("gfx/weapons/deagle.png")
    IMAGE_GROUND = pygame.image.load("gfx/weapons/deagle_g.png")
    MAGAZINE = 18
    COOLDOWN = 250
    RELOADTIME = 1000
    AMMO = Bullet

    def trigger(self, dest):
        if self.cooldown <= 0:
            # jeżeli magazynek jest pusty rozpłacz się
            if self.magazine <= 0:
                return
            # 1 pocisk
            vec = Vec2((0.0, 12.0)).rotate(self.owner.rotation + 30)
            position = self.position + vec
            velocity = (dest - position).unit() * 0.5
            self.projectiles.append(self.AMMO(position, velocity, self.owner))
            # 2 pocisk
            vec = Vec2((0.0, 12.0)).rotate(self.owner.rotation - 30)
            position = self.position + vec
            velocity = (dest - position).unit() * 0.5
            self.projectiles.append(self.AMMO(position, velocity, self.owner))
            # odjęcie pocisków z magazynka
            self.magazine -= 2
            self.cooldown = self.COOLDOWN
