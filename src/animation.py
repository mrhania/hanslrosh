# -*- coding: utf-8 -*-
"""Moduł zarządzający animacjami"""
import pygame


class Animation:
    # czas trwania pojedyńczej klatki (w milisekundach)
    DELAY = 100

    def __init__(self, image):
        # lista powierzchni z poszczególnymi klatkami
        self.frames = []
        # aktualnie wyświetlana klatka
        self.current = 0
        # czas pozostały do zmiany klatki
        self.time = 0
        # rozbicie obrazka na poszczególne klatki animacji
        (width, height) = image.get_size()
        for i in range(width / height):
            offset = pygame.Rect(height * i, 0, height, height)
            self.frames.append(image.subsurface(offset))

    def update(self, delta):
        # zaktualizuj czas klatki
        self.time -= delta
        # jeżeli nadeszła odpowiednia pora to zmień klatkę i odnów czas
        if self.time <= 0:
            self.current = (self.current + 1) % len(self.frames)
            self.time += Animation.DELAY

    def draw(self, surface, position, rotation=None):
        frame = self.frames[self.current]
        # jeżeli masz dodatkowo obrócić obrazek to zrób to
        if rotation:
            frame = pygame.transform.rotate(frame, rotation)
        # wyświetl obrazek na zadanej pozycji
        rect = frame.get_rect()
        rect.center = position
        surface.blit(frame, rect)
