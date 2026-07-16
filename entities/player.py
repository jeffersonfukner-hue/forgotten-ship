import pygame

from entities.entity import Entity


class Player(Entity):

    def __init__(self, x: float, y: float):
        super().__init__(x=x, y=y, width=32, height=32,)
        self.speed = 250

    def update(self, dt: float):
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

        self.x = max(100, min(self.x, 668))
        self.y = max(80, min(self.y, 488))

    def draw(self, screen):
        pygame.draw.rect(screen, (70, 150, 150),
                         (self.x, self.y, self.width, self.height),)
