import pygame

TOP = "top"
BOTTOM = "bottom"
LEFT = "left"
RIGHT = "right"


class Door:

    def __init__(self, x: int, y: int, width: int, height: int, side, target_room: str | None = None,):

        self.trigger_height = 12

        self.rect = pygame.Rect(x, y, width, height,)

        self.side = side
        self.trigger = self.build_trigger()

        self.build_draw_rect = self.build_draw_rect()

        self.target_room = target_room

        self.state = "closed"

        self.entry_point = pygame.Vector2(self.rect.centerx, self.rect.bottom)

    def build_trigger(self):

        if self.side == TOP:

            return pygame.Rect(self.rect.left, self.rect.bottom, self.rect.width, self.trigger_height,)

        elif self.side == BOTTOM:

            return pygame.Rect(self.rect.left, self.rect.top - self.trigger_height, self.rect.width, self.trigger_height,)

        elif self.side == LEFT:

            return pygame.Rect(self.rect.right, self.rect.top, self.trigger_height, self.rect.height,)

        elif self.side == RIGHT:

            return pygame.Rect(self.rect.left - self.trigger_height, self.rect.top, self.trigger_height, self.rect.height,)

        raise ValueError(f"Lado Inválido:{self.side}")

    def build_draw_rect(self):

        self.draw_rect = self.rect.copy()

        if self.side == TOP:
            self.draw_rect.y += 10

        elif self.side == BOTTOM:
            self.draw_rect.y -= 10

        elif self.side == LEFT:
            self.draw_rect.x += 10

        elif self.side == RIGHT:
            self.draw_rect.x -= 10

    def draw(self, screen: pygame.Surface) -> None:

        color = ((70, 180, 70)
                 if self.state == "open"
                 else (180, 120, 40))

        pygame.draw.rect(screen, color, self.draw_rect,)

    def collides(self, player) -> bool:

        return self.trigger.colliderect(player.rect)

    def open(self) -> None:

        self.state = "open"

    def close(self) -> None:

        self.state = "closed"
