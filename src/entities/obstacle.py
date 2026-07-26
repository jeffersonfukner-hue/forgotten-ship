import pygame

from src import settings
from src.entities.entity import Entity


class Obstacle(Entity):

    def __init__(self, x: float, y: float, width: int, height: int,
                 destructible: bool = False, hp: int = 0) -> None:
        super().__init__(x=x, y=y, width=width, height=height)

        self.original_width: int = width
        self.original_height: int = height

        self.destructible: bool = destructible

        if destructible:
            self.max_hp: int = hp
            self.hp: int = hp
            self.color: tuple = (150, 120, 60)  # tom marrom/dourado: sinaliza "destrutivel"
        else:
            self.max_hp: int = 0
            self.hp: int = 0
            self.color: tuple = (110, 115, 125)  # cinza metalico: fixo, indestrutivel

        self.is_dead: bool = False  # so relevante para destrutiveis; fixo nunca fica True
        self.damage_cooldown: float = 0.0  # evita corrosao instantanea por multiplos inimigos no mesmo frame

    def take_damage(self, amount: int) -> None:

        if not self.destructible or self.is_dead or self.damage_cooldown > 0:
            return

        self.hp -= amount
        self.damage_cooldown = settings.OBSTACLE_DAMAGE_COOLDOWN

        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True

    def update(self, dt: float) -> None:

        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt

        # encolhe visualmente conforme perde HP, ate sumir de vez
        if self.destructible and self.max_hp > 0:
            ratio = max(0.05, self.hp / self.max_hp)  # nunca zera de vez, encolhe ate quase sumir
            self.rect.width = max(1, int(self.original_width * ratio))
            self.rect.height = max(1, int(self.original_height * ratio))
    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:

        screen_rect = self.rect.copy()
        screen_rect.x -= camera_x
        screen_rect.y -= camera_y

        pygame.draw.rect(screen, self.color, screen_rect)
        pygame.draw.rect(screen, (60, 63, 70), screen_rect, width=2)