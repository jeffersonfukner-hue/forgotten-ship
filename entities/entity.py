import pygame


class Entity:
    def __init__(self, x: float, y: float, width: int, height: int) -> None:

        self.x: float = x
        self.y: float = y
        self.width: int = width
        self.height: int = height

        self.rect: pygame.Rect = pygame.Rect(
            self.x, self.y, self.width, self.height)

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        pass
