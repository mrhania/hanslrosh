# -*- coding: utf-8 -*-
"""
Moduł główny.
"""

import sys
import pygame

sys.path.append("src/")

import level
import camera
import particles
import fov
import hud
import menu
screen = None
clock = None


def init():
    """Procedura inicjująca moduły i tworząca podstawowe obiekty."""
    pygame.init()
    pygame.font.init()

    global screen, clock, level
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((camera.width, camera.height))
    pygame.display.set_caption("Hanslrosh")
    level.init(screen, 100, 100)
    hud.init()
    menu.init()


def update(delta):
    """Procedura zajmująca się aktualizacją logiki gry."""
    fps = round(1.0 / delta * 1000.0)
    pygame.display.set_caption("Hanslrosh (" + str(fps) + " fps)")
    # obsługa wydarzeń
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            exit()
    # obsługa klawiatury
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        menu.kind = "main menu"
    if keys[pygame.K_SPACE]:
        level.create()
    # aktualizacja menu
    menu.update(delta, events)
    # reszta dzieje się tylko jeżeli w menu uruchomiono grę
    if menu.kind == "game":
        # aktualizacja obiektów
        level.update(delta)
        particles.update(delta)
        # aktualizacja interfejsu
        hud.update(delta)


def draw():
    """Procedura zajmująca się rysowaniem wszystkich obiektów."""
    # wyczyszczenie sceny
    screen.fill((0, 0, 0))
    # narysowanie menu
    menu.draw(screen)
    if menu.kind == "game":
        # rysowanie obiektów w grze
        level.draw(screen)
        particles.draw(screen)
        fov.draw(screen)
        # rysowanie inteferjsu
        hud.draw(screen)
    # podmiana buforów
    pygame.display.update()


def main():
    # pętla główna
    init()
    while True:
        # ograniczenie na ilość klatek
        delta = clock.tick(60)

        update(delta)
        draw()


if __name__ == "__main__":
    main()
