import pygame

from src import settings
from src.entities.entity import Entity


class Enemy(Entity):

    def __init__(self, x: float, y: float, enemy_type: str = "weak") -> None:

        config = settings.ENEMY_TYPES[enemy_type]

        super().__init__(x=x, y=y, width=config["width"], height=config["height"])

        # --- combate ---
        self.enemy_type: str = enemy_type
        self.max_hp: int = config["hp"]
        self.hp: int = self.max_hp
        self.is_dead: bool = False

        # --- movimento ---
        self.speed: int = config["speed"]

        # --- visual ---
        self.color: tuple = config["color"]

    # ==================================================================
    # COMBATE
    # ==================================================================

    def take_damage(self, amount: int) -> None:

        if self.is_dead:
            return

        self.hp -= amount

        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True  # sinaliza para GameScene remover da lista de inimigos

    # ==================================================================
    # ATUALIZACAO POR FRAME
    # ==================================================================

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

    # ==================================================================
    # DESENHO
    # ==================================================================

    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:

        screen_rect = self.rect.copy()
        screen_rect.x -= camera_x
        screen_rect.y -= camera_y

        pygame.draw.rect(screen, self.color, screen_rect,)

        self.draw_hp_bar(screen, screen_rect)

    def draw_hp_bar(self, screen: pygame.Surface, screen_rect: pygame.Rect) -> None:

        bar_width = screen_rect.width
        bar_height = 3
        bar_x = screen_rect.x
        bar_y = screen_rect.y - bar_height - 2  # um pouco acima do topo do inimigo

        hp_ratio = self.hp / self.max_hp

        pygame.draw.rect(screen, (80, 30, 30),
                          (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (60, 180, 90),
                          (bar_x, bar_y, bar_width * hp_ratio, bar_height))