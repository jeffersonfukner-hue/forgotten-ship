import pygame

from src.entities.entity import Entity


class Enemy(Entity):

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x=x, y=y, width=28, height=28)

        self.speed: int = 80
        self.hp: int = 20
        self.is_dead: bool = False

    def take_damage(self, amount: int) -> None:
        if self.is_dead:
            return

        self.hp -= amount

        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True  # sinaliza para GameScene remover da lista de inimigos

    def update(self, dt: float, target_x: float, target_y: float, others: list) -> None:

        direction = pygame.Vector2(
            target_x - self.x, target_y - self.y)

        if direction.length_squared() > 0:
            direction = direction.normalize()

        separation = pygame.Vector2()

        for other in others:
            if other is self:
                continue

            if self.rect.colliderect(other.rect):
                # empurra na direcao oposta ao inimigo sobreposto
                push = pygame.Vector2(self.x - other.x, self.y - other.y)

                if push.length_squared() > 0:
                    separation += push.normalize()

        if separation.length_squared() > 0:
            separation = separation.normalize()
            direction = (direction + separation)

            if direction.length_squared() > 0:
                direction = direction.normalize()

        self.x += direction.x * self.speed * dt
        self.y += direction.y * self.speed * dt

        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, (180, 60, 60), self.rect,)
