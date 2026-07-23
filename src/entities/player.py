import pygame

from src.entities.entity import Entity


class Player(Entity):

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x=x, y=y, width=32, height=32,)

        self.state: str = "walking"

        self.speed: int = 250

        self.room: "Room | None" = None

        self.target_position: pygame.Vector2 | None = None

        self.current_door: "Door | None" = None

        self.room_change_requested: bool = False

        self.path: list[pygame.Vector2] = []

        self.alpha: int = 255
        self.door_leg_start: pygame.Vector2 | None = None
        self.door_thickness: float = 0.0

        self.max_hp: int = 100
        self.hp: int = self.max_hp
        self.is_dead: bool = False

        self.damage_cooldown: float = 0.0
        self.damage_cooldown_time: float = 1.0  # 1s de invencibilidade após levar dano

        self.knockback_force: int = 220

        self.shoot_cooldown: float = 0.0
        self.shoot_interval: float = 0.8  # segundos entre disparos automaticos

        # raio unico: percepcao de inimigos e alcance do tiro
        self.range_radius: float = 100

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

    def ready_to_shoot(self) -> bool:

        return self.shoot_cooldown <= 0

    def confirm_shot(self) -> None:
        self.shoot_cooldown = self.shoot_interval

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

    def take_damage(self, amount: int) -> None:

        if self.is_dead or self.damage_cooldown > 0:
            return  # ainda invencivel, ignora o dano

        self.hp -= amount
        self.damage_cooldown = self.damage_cooldown_time

        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True

    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:

        # posicao na tela = posicao no mundo menos o deslocamento da camera
        screen_pos = (self.rect.x - camera_x, self.rect.y - camera_y)

        self.draw_range_indicator(screen, camera_x, camera_y)

        if self.alpha >= 255:
            pygame.draw.rect(
                screen, (70, 150, 150), (*screen_pos, self.rect.width, self.rect.height),)
            return

        surface = pygame.Surface(
            (self.rect.width, self.rect.height), pygame.SRCALPHA)

        pygame.draw.rect(
            surface, (70, 150, 150, self.alpha), surface.get_rect(),)

        screen.blit(surface, screen_pos)

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
