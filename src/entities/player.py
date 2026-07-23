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

    def update(self, dt: float) -> None:

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

    def draw(self, screen: pygame.Surface) -> None:

        if self.alpha >= 255:
            pygame.draw.rect(screen, (70, 150, 150), self.rect,)
            return

        surface = pygame.Surface(
            (self.rect.width, self.rect.height), pygame.SRCALPHA)

        pygame.draw.rect(
            surface, (70, 150, 150, self.alpha), surface.get_rect(),)

        screen.blit(surface, self.rect.topleft)
