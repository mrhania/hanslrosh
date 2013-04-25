# -*- coding: utf-8 -*-
import pygame
import creature
import camera
import tile
from entity import Manager
from entity import Entity
from vector import Vec2

# standardowe rodzaje cząsteczek
SMOKE = pygame.image.load("gfx/particles/smoke.png")
PUFF = pygame.image.load("gfx/particles/puff.png")
EXPERIENCE = pygame.image.load("gfx/particles/exp.png")
BLOOD = [
    pygame.image.load("gfx/particles/blood_1.png"),
    pygame.image.load("gfx/particles/blood_2.png"),
    pygame.image.load("gfx/particles/blood_3.png"),
    pygame.image.load("gfx/particles/blood_4.png")
]
BONES = [
    pygame.image.load("gfx/particles/bones_1.png"),
    pygame.image.load("gfx/particles/bones_2.png")
]

# lista wszystkich znajdujących się w grze cząsteczek
container = Manager((tile.SIZE, tile.SIZE), (camera.width, camera.height))


def update(delta):
    container.update(delta)


def draw(surface):
    container.draw(surface)


class Particle(Entity):
    RADIUS = 3
    LIFETIME = 1000

    def __init__(self, position, velocity=None):
        super(Particle, self).__init__()
        self.position = position
        self.velocity = velocity if velocity else Vec2.random() * 0.1
        self.lifetime = self.LIFETIME
        self.currenttime = self.lifetime

        container.add(self)

    def update(self, delta):
        super(Particle, self).update(delta)
        self.currenttime -= delta
        if self.currenttime <= 0:
            self.kill()


class Puff(Particle):
    IMAGE = PUFF
    LIFETIME = 500


class ExpParticle(Particle):
    IMAGE = EXPERIENCE
    LIFETIME = 1000

    def __init__(self, position, amount):
        super(ExpParticle, self).__init__(position, None)
        self.velocity = Vec2((0.0, 0.0))
        self.amount = amount

    def update(self, delta):
        super(ExpParticle, self).update(delta)
        # przesuń cząsteczkę o odpowiedni wektor
        line = creature.Player().position - self.position
        self.velocity = line.unit() * 0.5
        if line.length() <= self.RADIUS + creature.Player().RADIUS:
            # dodaj graczowi doświadczenie
            creature.Player().points += self.amount
            # zabij się
            self.kill()
