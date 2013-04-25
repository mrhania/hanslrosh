# -*- coding: utf-8 -*-
import pygame
from pygame import Rect


class Quadtree(object):
    """Struktura rekurencyjna do sprawnego zarządzania obiektami."""

    def __init__(self, rect):
        # wartość węzła
        self.items = []
        # ramka węzła
        self.rect = rect
        # poddrzewa
        self.nw = None
        self.ne = None
        self.sw = None
        self.se = None

    def append(self, item):
        """Dodaje nowy element do drzewa czwórkowego."""

        # sprawdź czy się da to w ogóle włożyć
        if not self.rect.contains(item.rect):
            return

        size = (self.rect.width / 2, self.rect.height / 2)
        #  NW
        rect = Rect(self.rect.topleft, size)
        if rect.contains(item.rect):
            if not self.nw:
                self.nw = Quadtree(rect)
            self.nw.append(item)
            return
        # NE
        rect = Rect(self.rect.midtop, size)
        if rect.contains(item.rect):
            if not self.ne:
                self.ne = Quadtree(rect)
            self.ne.append(item)
            return
        # SW
        rect = Rect(self.rect.midleft, size)
        if rect.contains(item.rect):
            if not self.sw:
                self.sw = Quadtree(rect)
            self.sw.append(item)
            return
        # SE
        rect = Rect(self.rect.center, size)
        if rect.contains(item.rect):
            if not self.se:
                self.se = Quadtree(rect)
            self.se.append(item)
            return
        # do żadnego nie pasuje to dodaj tutaj
        #self.items.append(item)

    def collide(self, obj):
        """Sprawdza kolizję jedego obiektu z drugim."""
        # jak obiekt nie jest nawet w ramce to wyjdź
        if not self.rect.colliderect(obj.rect):
            return False

        # sprawdź kolizję ze wszystkimi obiektami w węźle
        for item in self.items:
            if item == obj:
                continue
            if (item.position - obj.position).length() <= 32:
                return True

        # idź rekurencyjnie po drzewie
        if self.nw and self.nw.collide(obj):
            return True
        if self.ne and self.ne.collide(obj):
            return True
        if self.sw and self.sw.collide(obj):
            return True
        if self.se and self.se.collide(obj):
            return True
        return False
"""
    def draw(self, surface):
        topleft = camera.screen_pos(Vec2(self.rect.topleft)).tuplify()
        size = self.rect.size
        pygame.draw.rect(surface, (255, 0, 0), Rect(topleft, size), 1)

        if self.nw:
            self.nw.draw(surface)
        if self.ne:
            self.ne.draw(surface)
        if self.sw:
            self.sw.draw(surface)
        if self.se:
            self.se.draw(surface)
"""
