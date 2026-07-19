import pygame

from src.entities.entity import Entity


class TestEntity(Entity):

    def __init__(self, x: float, y: float):
        super().__init__(x, y, 80, 80)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255),
                         (self.x, self.y, self.width, self.height),)
