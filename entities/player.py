import pygame

from entities.entity import Entity


class Player(Entity):

    def __init__(self, x: float, y: float):
        super().__init__(x=x, y=y, width=32, height=32,)

        self.state = "walking"

        self.speed = 250

        self.room = None

    def update(self, dt: float):

        if self.state != "walking":
            return

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

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, (70, 150, 150), self.rect,)
