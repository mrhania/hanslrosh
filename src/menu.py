# -*- coding: utf-8 -*-

import pygame
import pickle
import level
import creature

try:
    SCORES = pickle.load(open("scores.dat", "rb"))
except:
    SCORES = [{
        "score": 0,
        "name": "---"
    }]

BACKGROUND = None
CREDITS = None
FONT = None
HIGHSCORES = None

WAITTIME = 150

kind = None

selected = 0
waittime = 0
OPTIONS = ["new game", "credits", "high scores", "exit"]
RENDERED = None
RENDEREDS = None


def init():
    global BACKGROUND, FONT
    global RENDERED, RENDEREDS
    global kind, selected
    global CREDITS

    # wczytanie zasobów
    BACKGROUND = pygame.image.load("gfx/menu.png")
    CREDITS = pygame.image.load("gfx/credits.png")
    FONT = pygame.font.Font("font/impact.ttf", 30)
    # prerenderowanie obrazków
    color = (255, 255, 255)
    RENDERED = map(lambda text: FONT.render(text, True, color), OPTIONS)
    color = (255, 0, 0)
    RENDEREDS = map(lambda text: FONT.render(text, True, color), OPTIONS)
    # wyrenderuj początkową tabelkę wyników
    highscores()
    # na początku jesteśmy w menu głównym
    kind = "main menu"
    selected = 0


def highscores():
    global HIGHSCORES

    HIGHSCORES = []
    # wydrukuj tylko pierwsze 10 najwyższych wyników
    trimmed = sorted(SCORES, key=lambda score: -score["score"])[0:10]
    for score in trimmed:
        text = "%012s: %010d" % (score["name"], score["score"])
        HIGHSCORES.append(FONT.render(text, True, (255, 255, 255)))


def update(delta, events):
    global selected, waittime, kind
    waittime -= delta

    if waittime > 0:
        return

    keys = pygame.key.get_pressed()
    if kind == "main menu":
        # nawigowanie po opcjach
        if keys[pygame.K_UP]:
            selected = (selected - 1) % len(OPTIONS)
            waittime = WAITTIME
        if keys[pygame.K_DOWN]:
            selected = (selected + 1) % len(OPTIONS)
            waittime = WAITTIME
        # wybór jednej z opcji
        if keys[pygame.K_RETURN]:
            if OPTIONS[selected] == "exit":
                pickle.dump(SCORES, open("scores.dat", "wb"))
                exit()
            if OPTIONS[selected] == "credits":
                kind = "credits"
                waittime = WAITTIME
            if OPTIONS[selected] == "high scores":
                kind = "scores"
                waittime = WAITTIME
            if OPTIONS[selected] == "new game":
                # wygeneruj plansze od 1 poziomu
                level.create(1)
                # zresetuj gracza
                creature.Player().reset()
                kind = "game"
        return

    if kind == "credits" or kind == "scores":
        if keys[pygame.K_RETURN]:
            kind = "main menu"
            waittime = WAITTIME

    if kind == "end":
        endgame(events)


inputtext = ""


def endgame(events):
    global inputtext
    global kind
    global waittime

    for e in events:
        key = None
        if e.type == pygame.KEYDOWN:
            key = e.key

        if not key:
            return

        if key == pygame.K_BACKSPACE:
            inputtext = inputtext[0:-1]

        if ord('a') <= key <= ord('z'):
            inputtext += chr(key)

        if key == pygame.K_RETURN:
            # koniec zabawy, dodaj do wynikow i czesc
            SCORES.append({
                "name": inputtext,
                "score": creature.Player().points
            })
            highscores()
            kind = "main menu"
            waittime = WAITTIME

        if key == pygame.K_ESCAPE:
            # widocznie koleś nie chce uwiecznić swojego wyniku
            kind = "main menu"
            waittime = WAITTIME


def draw(surface):
    """Rysuje menu na zadanej powierzchni."""

    if kind == "main menu":
        # rysowanie tła...
        surface.blit(BACKGROUND, (0, 0))
        # ... i tekstów
        for i in range(len(OPTIONS)):
            pos = (10, i * (FONT.get_height() + 5) + 100)
            surf = RENDEREDS[i] if i == selected else RENDERED[i]
            surface.blit(surf, pos)

    if kind == "credits":
        surface.blit(CREDITS, (0, 0))

    if kind == "scores":
        surface.blit(BACKGROUND, (0, 0))
        for i in range(len(HIGHSCORES)):
            pos = (10, i * (FONT.get_height() + 5) + 30)
            surface.blit(HIGHSCORES[i], pos)

    if kind == "end":
        surface.blit(BACKGROUND, (0, 0))

        points = creature.Player().points
        line1 = "You have managed to get %d points." % (points,)
        line1b = FONT.render(line1, True, (255, 255, 255))
        line2 = "Insert your name: "
        line2b = FONT.render(line2, True, (255, 255, 255))
        name = FONT.render(inputtext, True, (255, 255, 255))

        surface.blit(line1b, (10, 100))
        surface.blit(line2b, (10, 100 + FONT.get_height() + 5))
        surface.blit(name, (10, 100 + 2 * (FONT.get_height() + 5)))
