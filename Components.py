import pygame
from pygame import Vector2

class CTransform:
    def __init__(self, pos : Vector2, velocity : Vector2, angle: float):
        self.pos = pos
        self.velocity = velocity
        self.angle = angle

class CShape:
    def __init__(self, center, width, height, color : pygame.Color):
        self.rect = pygame.FRect(0,0,width,height)
        self.rect.center = center
        self.surf = pygame.Surface((width, height))
        self.color = color
        self.surf.fill(color)

class CInput:
    def __init__(self):
        self.up = False
        self.left = False
        self.right = False
        self.down = False

class CGravity:
    def __init__(self, g: Vector2):
        self.gravity = g

class CTimer:
    def __init__(self, end: int):
        self.run = False
        self.count = 0
        self.end = end
        self.end_flag = False

class CAnimation:
    def __init__(self):
        self.anime_list = []

class CScoreMarker:
    def __init__(self):
        self.marker = False