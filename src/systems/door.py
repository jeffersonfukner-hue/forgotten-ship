import pygame

from src.entities.player import Player

TOP: str = "top"
BOTTOM: str = "bottom"
LEFT: str = "left"
RIGHT: str = "right"
SPAWN_OFFSET: int = 40


class Door:

    def __init__(self, id: int, x: int, y: int, width: int, height: int, side: str, target_door: int | None = None,):

        # --- identidade e geometria basica ---
        self.id: int = id
        self.trigger_height: int = 12

        self.rect: pygame.Rect = pygame.Rect(x, y, width, height,)

        self.side: str = side
        self.trigger: pygame.Rect = self.build_trigger()

        self.build_draw_rect()

        self.target_door: int | None = target_door

        # --- estado visual de transicao (aberta/fechada) ---
        self.state: str = "closed"

        # --- estados de bloqueio (afetam colisao e feedback visual) ---
        self.locked: bool = False  # quando True, a porta nao reage ao trigger do player
        self.reentry_blocked: bool = False  # True quando a sala de destino esta sem reentradas

    # --- controle de bloqueio por horda ativa ---

    def lock(self) -> None:

        self.locked = True

    def unlock(self) -> None:

        self.locked = False

    # --- geometria derivada (trigger e retangulo de desenho) ---

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

    def get_thickness(self) -> float:

        # profundidade real da porta, usada para calcular o fade de travessia do player
        if self.side in (TOP, BOTTOM):
            return self.rect.height

        return self.rect.width

    # --- pontos de navegacao (entrada, alinhamento, spawn) ---

    def get_entry_target(self, player_width: int, player_height: int) -> pygame.Vector2:

        offset = 40

        if self.side == TOP:
            return pygame.Vector2(self.rect.centerx - player_width / 2, self.rect.centery - offset,)

        if self.side == BOTTOM:
            return pygame.Vector2(self.rect.centerx - player_width / 2, self.rect.centery + offset,)

        if self.side == LEFT:
            return pygame.Vector2(self.rect.centerx - offset, self.rect.centery - player_height / 2,)

        return pygame.Vector2(self.rect.centerx + offset, self.rect.centery - player_height / 2,)

    def get_alignment_point(self, current_x: float, current_y: float, player_width: int, player_height: int) -> pygame.Vector2:

        # alinha o eixo perpendicular ao movimento antes de entrar reto na porta
        if self.side in (TOP, BOTTOM):
            return pygame.Vector2(self.rect.centerx - player_width / 2, current_y)

        return pygame.Vector2(current_x, self.rect.centery - player_height / 2)

    def get_spawn_position(self) -> pygame.Vector2:

        if self.side == TOP:
            return pygame.Vector2(self.rect.centerx, self.rect.centery + SPAWN_OFFSET,)

        if self.side == BOTTOM:
            return pygame.Vector2(self.rect.centerx, self.rect.centery - SPAWN_OFFSET,)

        if self.side == LEFT:
            return pygame.Vector2(self.rect.centerx + SPAWN_OFFSET, self.rect.centery,)

        return pygame.Vector2(self.rect.centerx - SPAWN_OFFSET, self.rect.centery,)

    # --- colisao e estado de transicao ---

    def collides(self, player: Player) -> bool:

        if self.locked:
            return False  # porta trancada nunca colide, mesmo com o trigger sobreposto

        return self.trigger.colliderect(player.rect)

    def open(self) -> None:

        self.state = "open"

    def close(self) -> None:

        self.state = "closed"

    # --- desenho ---

    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:

        # cor reflete o estado de bloqueio, com prioridade: reentrada > trancada > aberta/fechada
        if self.reentry_blocked:
            color = (100, 40, 130)  # roxo escuro: sala de destino sem reentradas
        elif self.locked:
            color = (140, 40, 40)  # vermelho escuro: porta trancada, precisa limpar a sala
        elif self.state == "open":
            color = (70, 180, 70)
        else:
            color = (180, 120, 40)

        screen_rect = self.draw_rect.copy()
        screen_rect.x -= camera_x
        screen_rect.y -= camera_y

        pygame.draw.rect(screen, color, screen_rect,)

        font = pygame.font.Font(None, 24)

        text = font.render(str(self.id), True, (255, 255, 255))

        text_rect = text.get_rect(center=screen_rect.center)

        screen.blit(text, text_rect)