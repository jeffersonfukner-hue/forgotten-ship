import pygame

from src.entities.entity import Entity


class FloatingText(Entity):

    def __init__(self, x: float, y: float, text: str, color: tuple = (255, 80, 80)) -> None:
        super().__init__(x=x, y=y, width=0, height=0)

        self.text: str = text
        self.color: tuple = color

        self.lifetime: float = 0.8  # segundos ate desaparecer
        self.age: float = 0.0

        self.rise_speed: int = 40  # velocidade de subida, em pixels por segundo

        self.is_dead: bool = False

    def update(self, dt: float) -> None:

        self.age += dt
        self.y -= self.rise_speed * dt  # sobe continuamente

        if self.age >= self.lifetime:
            self.is_dead = True

    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:

        progress = self.age / self.lifetime
        alpha = int(255 * (1 - progress))  # desaparece gradualmente

        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, self.color)
        text_surface.set_alpha(alpha)

        screen_pos = (self.x - camera_x, self.y - camera_y)
        screen.blit(text_surface, screen_pos)