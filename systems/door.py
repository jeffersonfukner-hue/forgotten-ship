import pygame

from entities.player import Player

TOP = "top"
BOTTOM = "bottom"
LEFT = "left"
RIGHT = "right"


class Door:

    def __init__(self, x: int, y: int, width: int, height: int, side: str, target_room: int | None = None,):

        self.trigger_height: int = 12

        self.rect: pygame.Rect = pygame.Rect(x, y, width, height,)

        self.side: str = side
        self.trigger: pygame.Rect = self.build_trigger()

        self.build_draw_rect()

        self.target_room: int | None = target_room

        self.state: str = "closed"

    def build_trigger(self) -> pygame.Rect:

        if self.side == TOP:

            return pygame.Rect(self.rect.left, self.rect.bottom, self.rect.width, self.trigger_height,)

        elif self.side == BOTTOM:

            return pygame.Rect(self.rect.left, self.rect.top - self.trigger_height, self.rect.width, self.trigger_height,)

        elif self.side == LEFT:

            return pygame.Rect(self.rect.right, self.rect.top, self.trigger_height, self.rect.height,)

        elif self.side == RIGHT:

            return pygame.Rect(self.rect.left - self.trigger_height, self.rect.top, self.trigger_height, self.rect.height,)

        raise ValueError(f"Lado Inválido:{self.side}")

    def build_draw_rect(self) -> None:

        self.draw_rect: pygame.Rect = self.rect.copy()

        if self.side == TOP:
            self.draw_rect.y += 10

        elif self.side == BOTTOM:
            self.draw_rect.y -= 10

        elif self.side == LEFT:
            self.draw_rect.x += 10

        elif self.side == RIGHT:
            self.draw_rect.x -= 10

    def get_entry_target(self) -> pygame.Vector2:

        offset = 40

        if self.side == TOP:
            return pygame.Vector2(self.rect.centerx, self.rect.centery - offset,)

        if self.side == BOTTOM:
            return pygame.Vector2(self.rect.centerx, self.rect.centery + offset,)

        if self.side == LEFT:
            return pygame.Vector2(self.rect.centerx - offset, self.rect.centery,)

        return pygame.Vector2(self.rect.centerx + offset, self.rect.centery,)

    def draw(self, screen: pygame.Surface) -> None:

        color = ((70, 180, 70)
                 if self.state == "open"
                 else (180, 120, 40))

        pygame.draw.rect(screen, color, self.draw_rect,)

    def collides(self, player: Player) -> bool:

        return self.trigger.colliderect(player.rect)

    def open(self) -> None:

        self.state = "open"

    def close(self) -> None:

        self.state = "closed"
