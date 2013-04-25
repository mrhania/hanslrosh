# -*- coding: utf-8 -*-
"""
Moduł do rysowania elementów HUD.
"""
import pygame
import camera
import creature
import level
from collections import deque

# czcionki
_fontcounter = None
_fontlogger = None
# singleton gracza, tak żeby było łatwiej
_player = creature.Player()
# obrazki do pasków
_bars = None
# wskaźniki i odpowiadające im wyrenderowane bitmapy
_ammomagazine = -1
_ammomagazineb = pygame.Surface((0, 0))
_ammobackpack = -1
_ammobackpackb = pygame.Surface((0, 0))
# kondygnacja
_storey = -1
_storeyb = pygame.Surface((0, 0))
# punkty
_points = -1
_pointsb = pygame.Surface((0, 0))
# lista wiadomości do wyświetlenia
_logger = deque()


def init():
    global _fontcounter, _fontlogger
    global _bars
    _fontcounter = pygame.font.Font("font/dignity.ttf", 30)
    _fontlogger = pygame.font.Font("font/orbitronb.ttf", 15)
    _bars = pygame.image.load("gfx/bars.png")


def log(message, time=3000):
    surface = _fontlogger.render(message, False, (100, 255, 100))
    _logger.append({
        "surface": surface,
        "time": time,
    })


def clearlog():
    _logger.clear()


def debug(surface, messages):
    for i in range(len(messages)):
        rendered = _fontlogger.render(messages[i], False, (100, 255, 100))
        surface.blit(rendered, (0, i * _fontlogger.get_height()))


def update(delta):
    global _ammomagazine, _ammomagazineb
    global _ammobackpack, _ammobackpackb
    global _storey, _storeyb
    global _points, _pointsb
    # sprawdź czy nie trzeba zaktualizować bitmapy z amunicją w magazynku
    if _player.weapon.magazine != _ammomagazine:
        _ammomagazine = _player.weapon.magazine
        text = "%02d" % (_ammomagazine,)
        _ammomagazineb = _fontcounter.render(text, False, (255, 255, 255))
    # analogiczne dla nabojów w plecaku
    if _player.ammo[_player.weapon.NAME] != _ammobackpack:
        _ammobackpack = _player.ammo[_player.weapon.NAME]
        text = "%03d" % (_ammobackpack,)
        _ammobackpackb = _fontcounter.render(text, False, (255, 255, 255))
    # i to samo dla poziomu
    if level.storey != _storey:
        _storey = level.storey
        text = "storey -%d" % (_storey,)
        _storeyb = _fontlogger.render(text, False, (100, 255, 100))
    if _player.points != _points:
        _points = _player.points
        text = "%010d points" % (_points,)
        _pointsb = _fontlogger.render(text, False, (100, 255, 100))
    # zaktualizuj czas każdej wiadomości w kolejce
    for log in _logger:
        log["time"] -= delta
    while len(_logger) > 0 and _logger[0]["time"] <= 0:
        _logger.popleft()


def draw(surface):
    # rysowanie ilości naboi w magazynku
    position = (10, camera.height - _ammomagazineb.get_height())
    surface.blit(_ammomagazineb, position)
    # rysowanie ilości naboi w plecasiu
    position = (50, camera.height - _ammobackpackb.get_height())
    surface.blit(_ammobackpackb, position)
    # rysowanie poziomu
    position = (camera.width - _storeyb.get_width() - 10, 10)
    surface.blit(_storeyb, position)
    # rysowanie punktów
    position = (camera.width - _pointsb.get_width() - 10, 25)
    surface.blit(_pointsb, position)
    # pasek życia
    length = int(_player.hitpoints * 2.55) + 1
    rect = pygame.Rect(camera.width - 255 - 8, camera.height - 30, length, 25)
    surface.fill((255, 0, 0), rect)
    # pasek głodu
    length = int(_player.hunger * 2.55)
    rect = pygame.Rect(camera.width - 255 - 8, camera.height - 55, length, 25)
    surface.fill((length, min(255, 255 - length), 0), rect)
    # ładny (tzn. nie taki znowu ładny...) interfejs na paski
    surface.blit(_bars, (camera.width - 255 - 15, camera.height - 50 - 10))
    # rysowanie wiadomości z dziennka
    i = 0
    for log in _logger:
        surface.blit(log["surface"], (10, i * _fontlogger.get_height() + 10))
        i += 1
