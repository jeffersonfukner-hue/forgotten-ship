import pygame

from src.entities.entity import Entity


class Projectile(Entity):

    def __init__(self, x: float, y: float, direction: pygame.Vector2, damage: int = 10) -> None:
        super().__init__(x=x, y=y, width=8, height=8,)

        self.speed: int = 400
        self.damage: int = damage
        self.direction: pygame.Vector2 = direction
        self.is_dead: bool = False  # marcado para remocao ao atingir algo ou sair da sala

    def update(self, dt) -> None:
        self.x += self.direction.x * self.speed * dt
        self.y += self.direction.y * self.speed * dt

        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, (255, 220, 80), self.rect.center, 4,)
