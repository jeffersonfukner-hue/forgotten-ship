import pygame

from src.entities.entity import Entity


class Enemy(Entity):

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x=x, y=y, width=28, height=28)

        self.speed: int = 80

    def update(self, dt: float, target_x: float, target_y: float) -> None:

        direction = pygame.Vector2(
            target_x - self.x, target_y - self.y)

        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.x += direction.x * self.speed * dt
        self.y += direction.y * self.speed * dt

        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, (180, 60, 60), self.rect,)
