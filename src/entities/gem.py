import pygame

from src.entities.entity import Entity


class Gem(Entity):

    def __init__(self, x: float, y: float, value: float) -> None:

        # tamanho proporcional ao valor, com um minimo para nunca ficar invisivel
        size = max(4, min(14, int(value)))

        super().__init__(x=x, y=y, width=size, height=size)

        self.value: float = value
        self.is_dead: bool = False  # marcado para remocao ao ser coletada

        # --- efeito de arrasto: comeca parada, acelera ao ser "puxada" ---
        self.being_pulled: bool = False
        self.pull_speed: float = 0.0  # velocidade atual, cresce enquanto puxada

    def start_pull(self) -> None:

        self.being_pulled = True

    def update_pull(self, dt: float, target_x: float, target_y: float,
                     acceleration: float, max_speed: float) -> None:
        """Move a gema em direcao ao alvo, acelerando progressivamente
        ate a velocidade maxima - cria o efeito de 'arrasto' (devagar no
        inicio, rapido ao se aproximar)."""

        if not self.being_pulled:
            return

        direction = pygame.Vector2(
            target_x - self.rect.centerx, target_y - self.rect.centery)

        if direction.length_squared() == 0:
            return

        direction = direction.normalize()

        self.pull_speed = min(
            max_speed, self.pull_speed + acceleration * dt)

        self.x += direction.x * self.pull_speed * dt
        self.y += direction.y * self.pull_speed * dt

        self.rect.x = self.x
        self.rect.y = self.y

    def update(self, dt: float) -> None:
        pass  # movimento real acontece em update_pull, chamado explicitamente pela GameScene

    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:

        center = (self.rect.centerx - camera_x, self.rect.centery - camera_y)
        radius = self.rect.width / 2

        pygame.draw.circle(screen, (240, 210, 60), center, radius)
        pygame.draw.circle(screen, (255, 255, 255), center, radius, width=1)