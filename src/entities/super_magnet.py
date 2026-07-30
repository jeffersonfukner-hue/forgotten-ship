import pygame

from src.entities.entity import Entity


class SuperMagnet(Entity):
    """Pickup unico dropado por chefes (Mini-chefe, Chefe, Chefao) ao
    morrer - substitui a gema normal. So ao ser coletado (mesma logica
    de atracao/puxao da gema) e' que libera os 2 efeitos garantidos:
    +1 nivel em 3 power-ups ja equipados, e puxao automatico de todas
    as gemas da sala. Ver GameScene.update() para a logica de coleta."""

    SIZE = 20  # maior que qualquer gema normal, para ficar visualmente distinto

    def __init__(self, x: float, y: float) -> None:

        super().__init__(x=x, y=y, width=self.SIZE, height=self.SIZE)

        self.is_dead: bool = False  # marcado para remocao ao ser coletado

        # --- efeito de arrasto: mesmo padrao da Gem (comeca parado, acelera puxado) ---
        self.being_pulled: bool = False
        self.pull_speed: float = 0.0

    def start_pull(self) -> None:

        self.being_pulled = True

    def update_pull(self, dt: float, target_x: float, target_y: float,
                    acceleration: float, max_speed: float) -> None:
        """Identico ao update_pull da Gem - duplicado propositalmente aqui
        (em vez de herdar de Gem) porque SuperMagnet nao tem 'value' nem
        semantica de pontos - e' um pickup de evento, nao de progressao
        numerica, mesmo compartilhando a mecanica visual de arrasto."""

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

        # circulo maior e mais vibrante que a gema comum, com anel duplo (destaque visual)
        pygame.draw.circle(screen, (255, 215, 0), center, radius)
        pygame.draw.circle(screen, (255, 255, 255), center, radius, width=2)
        pygame.draw.circle(screen, (255, 215, 0), center, radius - 6, width=1)
