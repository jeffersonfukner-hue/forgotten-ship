import pygame

from src.entities.entity import Entity


class Projectile(Entity):

    def __init__(self, x: float, y: float, direction: pygame.Vector2,
                 damage: int = 10, max_range: float = 100, pierce: int = 1) -> None:
        super().__init__(x=x, y=y, width=8, height=8,)

        self.speed: int = 400
        self.damage: int = damage
        self.direction: pygame.Vector2 = direction
        self.is_dead: bool = False  # marcado para remocao ao atingir algo ou sair da sala

        self.max_range: float = max_range  # distancia maxima antes de desaparecer sozinho
        self.distance_traveled: float = 0.0

        # pierce = quantos inimigos o projetil ainda pode atingir antes de morrer
        # valor 1 = comportamento atual (morre no primeiro impacto); upgrade futuro de Penetracao aumenta isso
        self.pierce: int = pierce

    def update(self, dt) -> None:

        step = self.direction * self.speed * dt

        self.x += step.x
        self.y += step.y

        self.rect.x = self.x
        self.rect.y = self.y

        self.distance_traveled += step.length()

        if self.distance_traveled >= self.max_range:
            self.is_dead = True  # alcance maximo atingido, some mesmo sem acertar nada

    def register_hit(self) -> None:

        # chamado pela GameScene ao colidir com um inimigo
        self.pierce -= 1

        if self.pierce <= 0:
            self.is_dead = True

    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:

        screen_center = (
            self.rect.centerx - camera_x, self.rect.centery - camera_y)

        pygame.draw.circle(screen, (255, 220, 80), screen_center, 4,)
