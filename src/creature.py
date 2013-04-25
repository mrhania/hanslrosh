# -*- coding: utf-8 -*-
import pygame
import camera
import tile
import weapon
import level
import particles
import random
from vector import Vec2
from utils import Singleton
from animation import Animation
from entity import Entity


class Creature(Entity):
    """Bazowa klasa dla żywych obiektów w grze."""
    RADIUS = tile.SIZE / 2.0
    IMMUNETIME = 0
    DAMAGE = 0
    SPEED = 0

    def __init__(self):
        super(Creature, self).__init__()
        # żywotność postaci
        self.hitpoints = 100.0
        self.weapon = None
        self.immunetime = 0

    def collide(self):
        """Zwraca listę przeciwników z którymi koliduje."""
        # współrzędne kafla na którym stoi gracz
        tilex = int(self.position.x / tile.SIZE)
        tiley = int(self.position.y / tile.SIZE)

        # sprawdź czy kafel na którym stoi jest "legalny"
        if not (level.tiles[tilex][tiley] == tile.GROUND or
                level.tiles[tilex][tiley] == tile.PASSAGE or
                level.tiles[tilex][tiley] == tile.DOOR):
            return True

        return False

    def hit(self, damage):
        if self.immunetime > 0:
            return
        randdamage = (random.random() * 1.5) ** 2 * random.randint(-1, 1)
        self.hitpoints -= max(0, damage - randdamage * damage)
        # sprawdź czy istotce się nie zeszło
        if self.hitpoints <= 0.0:
            particles.ExpParticle(self.position.copy(), int(10 * self.DAMAGE * self.SPEED))
            self.kill()
        # krwawienie
        blood = random.choice(particles.BLOOD)
        rect = blood.get_rect()
        rect.center = self.position.tuplify()
        level.tilemap.blit(blood, rect)
        self.immunetime = self.IMMUNETIME

    def update(self, delta):
        super(Creature, self).update(delta)
        self.immunetime -= delta

    def draw(self, surface):
        # narysuj broń (jeśli jakąś posiadasz)
        if self.weapon:
            self.weapon.draw(surface)
        super(Creature, self).draw(surface)


class Player(Creature):
    __metaclass__ = Singleton
    IMAGE = pygame.image.load("gfx/creatures/human.png")
    ACTIONCOOLDOWN = 1000
    IMMUNETIME = 100

    def __init__(self):
        super(Player, self).__init__()
        self.reset()

    def reset(self):
        self.hitpoints = 100.0
        self.hunger = 0.0
        self.actioncooldown = 0
        self.points = 0

        self.ammo = {
            "ak47": 1000,
            "shotgun": 1000,
            "awp": 1000,
            "deagle": 1000
        }

    def use(self):
        """Metoda odpalana kiedy gracz wciśnie klawisz użycia."""
        # sprawdź czy niedawno przypadkiem nie wykonałeś jakiejś akcji
        if self.actioncooldown > 0:
            return
        self.actioncooldown = self.ACTIONCOOLDOWN
        # sprawdź najbliższy obiekt na którym stoi gracz
        used = None
        for item in level.items:
            if item == self.weapon:
                continue
            if (item.position - self.position).length() <= tile.SIZE:
                used = item
                break
        # jak znalazłeś jakiś przedmiot to fajno
        if used:
            # podniosłeś może broń?
            if isinstance(used, weapon.Weapon):
                used.owner = self
                self.weapon.owner = None
                self.weapon = used

    def update(self, delta):
        super(Player, self).update(delta)
        # aktualizacja "głodu"
        self.hunger = min(100.0, self.hunger + delta * 0.0005)
        # jak głód osiągnął swoje maksimum to odejmuj życie
        if self.hunger >= 100.0:
            self.hitpoints -= delta * 0.001
        # aktualizacja czasu na podejmowanie działań
        self.actioncooldown -= delta
        # obsługa klawiszy
        keys = pygame.key.get_pressed()
        self.velocity = Vec2((0.0, 0.0))
        # lista kolidujących przeciwników
        if keys[pygame.K_w]:
            self.velocity.y -= camera.speed
        if keys[pygame.K_s]:
            self.velocity.y += camera.speed
        if keys[pygame.K_a]:
            self.velocity.x -= camera.speed
        if keys[pygame.K_d]:
            self.velocity.x += camera.speed
        # gracz wcisnął klawisz akcji
        if keys[pygame.K_f]:
            self.use()
        # przeładowanie broni
        if keys[pygame.K_r] and self.weapon:
            self.weapon.reload()

        # jak gracz wcisnął mychę to strzelaj
        (clicked, _, _) = pygame.mouse.get_pressed()
        if clicked:
            dest = Vec2(camera.real(Vec2(pygame.mouse.get_pos())))
            self.weapon.trigger(dest)

        # liczenie obrotu
        center = Vec2((camera.width / 2, camera.height / 2))
        self.rotation = Vec2.angle(Vec2(pygame.mouse.get_pos()) - center,
                                   Vec2((0.0, -1.0)))

        camera.lookat(self)


class Zombie(Creature):
    """Tępe zombie, ślepo idące w stronę gracza."""
    IMAGE = pygame.image.load("gfx/creatures/zombie.png")
    RANGE = tile.SIZE + 2
    SPEED = 1.0
    DAMAGE = 0.8

    def __init__(self, position=None):
        super(Zombie, self).__init__()
        if position:
            self.position = position

    def collide(self):
        # kolizja standardowa (ze ścianami)
        result = super(Zombie, self).collide()
        if result:
            return True
        # sprawdź czy nie kolidujesz z jakimś ziomeczkiem
        return level.creatures.collide(self)

    def update(self, delta):
        super(Zombie, self).update(delta)

        # zombiak czuje mięso i zawsze idzie w kierunku gracza
        line = Player().position - self.position
        self.rotation = Vec2.angle(line, Vec2((0.0, -1.0)))
        self.velocity = line.unit() * 0.05 * self.SPEED
        # jak jest w zasięgu gracza to go kąsa
        if line.length() <= self.RANGE:
            Player().hit(self.DAMAGE)


class GlowingZombie(Zombie):
    """Trochę silniejsza wersja zwykłego zombiasza."""
    IMAGE = pygame.image.load("gfx/creatures/glowingzombie.png")
    SPEED = 1.2
    DAMAGE = 1.0

    def __init__(self, position=None):
        super(GlowingZombie, self).__init__(position)
        self.hitpoints = 300.0


class Skeleton(Zombie):
    """Łatwe do zabicia, ale bardzo szybkie bydlę. I gryzie mocno."""
    IMAGE = pygame.image.load("gfx/creatures/skeleton.png")
    SPEED = 2.0
    DAMAGE = 2.0

    def __init__(self, position=None):
        super(Skeleton, self).__init__(position)
        self.hitpoints = 50.0

    def hit(self, damage):
        randdamage = (random.random() * 1.5) ** 2 * random.randint(-1, 1)
        self.hitpoints -= max(0, damage - randdamage * 10)
        # sprawdź czy istotce się nie zeszło
        if self.hitpoints <= 0.0:
            particles.ExpParticle(self.position.copy(), 100)
            self.kill()
        # szkieleciak nie krawawi, tylu pluje resztkami kości
        bones = random.choice(particles.BONES)
        rect = bones.get_rect()
        rect.center = self.position.tuplify()
        level.tilemap.blit(bones, rect)
