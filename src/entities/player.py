import pygame

from typing import TYPE_CHECKING

from src import settings
from src.entities.entity import Entity

if TYPE_CHECKING:
    # imports usados apenas para checagem de tipos (Pylance), evitando import circular real
    from src.systems.room import Room
    from src.systems.door import Door

class Player(Entity):

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x=x, y=y, width=32, height=32,)

        # --- movimento e navegacao entre salas ---
        self.state: str = "walking"
        self.speed: int = 250
        self.room: "Room | None" = None
        self.target_position: pygame.Vector2 | None = None
        self.current_door: "Door | None" = None
        self.room_change_requested: bool = False
        self.path: list[pygame.Vector2] = []

        # --- fade ao atravessar portas ---
        self.alpha: int = 255
        self.door_leg_start: pygame.Vector2 | None = None
        self.door_thickness: float = 0.0

        # --- vida e vidas (sistema de continuar apos morrer) ---
        self.max_hp: int = settings.PLAYER_MAX_HP
        self.hp: int = self.max_hp
        self.max_lives: int = settings.PLAYER_MAX_LIVES
        self.lives: int = self.max_lives
        self.is_dead: bool = False

        # --- cooldowns de dano e knockback ---
        self.damage_cooldown: float = 0.0
        self.damage_cooldown_time: float = 1.0  # 1s de invencibilidade apos levar dano
        self.knockback_force: int = settings.PLAYER_KNOCKBACK_FORCE

        # --- combate: disparo automatico e alcance ---
        self.shoot_cooldown: float = 0.0
        self.shoot_interval: float = settings.PLAYER_SHOOT_INTERVAL
        self.range_radius: float = settings.PLAYER_RANGE_RADIUS
        self.shoot_damage: int = settings.PLAYER_SHOOT_DAMAGE  # pode aumentar com upgrades

        # --- progressao: pontos de drop e upgrades automaticos ---
        self.level: int = 0  # quantidade de upgrades ja conquistados
        self.drop_points: float = 0.0
        self.points_to_upgrade: float = settings.POINTS_PER_UPGRADE

    # ==================================================================
    # VIDA, MORTE E CONTINUAR
    # ==================================================================

    def take_damage(self, amount: int) -> None:

        if self.is_dead or self.damage_cooldown > 0:
            return  # ainda invencivel, ignora o dano

        self.hp -= amount
        self.damage_cooldown = self.damage_cooldown_time

        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True

    def revive(self) -> None:

        # usado ao continuar apos morrer: restaura HP e volta ao estado normal
        self.hp = self.max_hp
        self.is_dead = False

    def has_lives_left(self) -> bool:

        return self.lives > 0

    def consume_life(self) -> None:

        self.lives -= 1

    def apply_knockback(self, from_x: float, from_y: float) -> None:

        direction = pygame.Vector2(self.x - from_x, self.y - from_y)

        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        else:
            direction = direction.normalize()

        self.x += direction.x * self.knockback_force / 10
        self.y += direction.y * self.knockback_force / 10

        if self.room:  # respeita os limites da sala, mesmo apos empurrao
            left, top, right, bottom = self.room.get_bounds()
            self.x = max(left, min(self.x, right - self.width))
            self.y = max(top, min(self.y, bottom - self.height))

        self.rect.x = self.x
        self.rect.y = self.y

    # ==================================================================
    # COMBATE: DISPARO AUTOMATICO
    # ==================================================================

    def ready_to_shoot(self) -> bool:

        return self.shoot_cooldown <= 0

    def confirm_shot(self) -> None:

        self.shoot_cooldown = self.shoot_interval

    # ==================================================================
    # PROGRESSAO (DROPS E UPGRADES)
    # ==================================================================

    def add_drop_point(self, amount: float = 1) -> None:

        self.drop_points += amount

        if self.drop_points >= self.points_to_upgrade:
            self.drop_points -= self.points_to_upgrade
            self.level += 1

            # cada novo level exige mais pontos, na mesma proporcao de crescimento das ondas
            self.points_to_upgrade *= settings.UPGRADE_THRESHOLD_GROWTH

            self.apply_automatic_upgrade()

    def apply_automatic_upgrade(self) -> None:

        # upgrade minimo para provar o ciclo drop -> progresso -> mais forte
        # sera substituido por escolha de 3 opcoes em Sprint futura
        self.shoot_damage += settings.UPGRADE_DAMAGE_INCREMENT

    # ==================================================================
    # ATUALIZACAO POR FRAME
    # ==================================================================

    def update(self, dt: float) -> None:

        if self.is_dead:
            return  # jogador morto nao processa mais input nem movimento

        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt  # cooldown corre independente do estado

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt  # cooldown de tiro corre sempre, independente do estado

        if self.state == "walking":
            self.update_walking(dt)

        elif self.state == "entering_door":
            self.update_entering_door(dt)

    def update_walking(self, dt: float) -> None:

        keys = pygame.key.get_pressed()

        direction = pygame.Vector2()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction.x -= 1

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction.x += 1

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            direction.y -= 1

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            direction.y += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.x += direction.x * self.speed * dt
        self.y += direction.y * self.speed * dt

        if self.room:

            left, top, right, bottom = self.room.get_bounds()

            self.x = max(left, min(self.x, right - self.width),)
            self.y = max(top, min(self.y, bottom - self.height),)

            self.rect.x = self.x
            self.rect.y = self.y

    def update_entering_door(self, dt: float) -> None:

        if self.target_position is None:
            return

        direction = self.target_position - pygame.Vector2(self.x, self.y)

        if direction.length() < 2:

            self.x = self.target_position.x
            self.y = self.target_position.y

            self.rect.x = self.x
            self.rect.y = self.y

            if self.path:
                self.target_position = self.path.pop(0)

                if not self.path:
                    self._begin_final_leg()

                return

            self.target_position = None
            self.alpha = 255
            self.door_leg_start = None

            self.room_change_requested = True

            self.state = "walking"

            return

        direction = direction.normalize()

        self.x += direction.x * self.speed * dt
        self.y += direction.y * self.speed * dt

        self.rect.x = self.x
        self.rect.y = self.y

        if self.door_leg_start is not None:
            self._update_fade()

    # ==================================================================
    # NAVEGACAO ENTRE SALAS (transicao por portas)
    # ==================================================================

    def consume_room_change(self) -> bool:

        if self.room_change_requested:

            self.room_change_requested = False
            return True
        return False

    def start_door_sequence(self, waypoints: list[pygame.Vector2], door_thickness: float) -> None:

        self.path = list(waypoints)
        self.door_thickness = door_thickness
        self.target_position = self.path.pop(0)

    def _begin_final_leg(self) -> None:

        self.door_leg_start = pygame.Vector2(self.x, self.y)

    def _update_fade(self) -> None:

        if self.door_thickness <= 0:
            self.alpha = 0
            return

        traveled = (pygame.Vector2(self.x, self.y) -
                    self.door_leg_start).length()

        progress = traveled / self.door_thickness
        progress = max(0.0, min(progress, 1.0))

        self.alpha = int(255 * (1 - progress))

    # ==================================================================
    # DESENHO
    # ==================================================================

    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:

        # posicao na tela = posicao no mundo menos o deslocamento da camera
        screen_pos = (self.rect.x - camera_x, self.rect.y - camera_y)

        self.draw_range_indicator(screen, camera_x, camera_y)

        if self.alpha >= 255:
            pygame.draw.rect(
                screen, (70, 150, 150), (*screen_pos, self.rect.width, self.rect.height),)
        else:
            surface = pygame.Surface(
                (self.rect.width, self.rect.height), pygame.SRCALPHA)

            pygame.draw.rect(
                surface, (70, 150, 150, self.alpha), surface.get_rect(),)

            screen.blit(surface, screen_pos)

        self.draw_hp_bar(screen, screen_pos)

    def draw_hp_bar(self, screen: pygame.Surface, screen_pos: tuple) -> None:

        bar_width = self.rect.width
        bar_height = 4
        bar_x = screen_pos[0]
        bar_y = screen_pos[1] - bar_height - 4  # um pouco acima do topo do player

        hp_ratio = self.hp / self.max_hp

        pygame.draw.rect(screen, (80, 30, 30),
                          (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (60, 180, 90),
                          (bar_x, bar_y, bar_width * hp_ratio, bar_height))

    def draw_range_indicator(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:

        # circulo sempre visivel: percepcao de inimigos e alcance do tiro compartilham este raio
        center = (self.rect.centerx - camera_x, self.rect.centery - camera_y)

        # desenhado numa surface separada com alpha, para ficar discreto (nao solido)
        diameter = int(self.range_radius * 2)
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

        pygame.draw.circle(
            surface, (150, 200, 220, 18), (self.range_radius, self.range_radius), self.range_radius,)
        pygame.draw.circle(
            surface, (150, 200, 220, 45), (self.range_radius, self.range_radius), self.range_radius, width=2,)

        screen.blit(
            surface, (center[0] - self.range_radius, center[1] - self.range_radius))