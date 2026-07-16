import pygame


class Entity:
    def __init__(self, x: float, y: float, width: int, height: int):

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, dt: float):
        pass

    def draw(self, screen):
        pass
