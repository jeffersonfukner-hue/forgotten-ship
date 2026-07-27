import math

import pygame

from src import settings
from src.entities.entity import Entity


class Saber(Entity):
    """Lamina giratoria que orbita o player. Cada instancia representa
    UMA lamina; a quantidade de laminas ativas e controlada pela
    GameScene, que cria/recria instancias conforme o nivel de
    'sabre_quantidade' do player muda."""

    def __init__(self, angle_offset: float) -> None:

        # tamanho fixo da lamina - nao muda com upgrade (so dano, velocidade e quantidade mudam)
        size = 16
        super().__init__(x=0, y=0, width=size, height=size)

        # angulo inicial distinto por lamina, para ficarem espacadas ao redor do player
        self.angle: float = angle_offset

        # rastreia o ultimo instante em que cada inimigo foi atingido por ESTA lamina,
        # para nao aplicar dano em todo frame de sobreposicao (mesmo espirito do
        # cooldown de corrosao em obstaculos destrutiveis)
        self._hit_cooldowns: dict = {}

    # ==================================================================
    # ATUALIZACAO POR FRAME
    # ==================================================================

    def update(self, dt: float, player, rotation_speed: float) -> None:

        self.angle = (self.angle + rotation_speed * dt) % 360

        radians = math.radians(self.angle)

        center_x = player.rect.centerx + \
            math.cos(radians) * settings.SABER_ORBIT_RADIUS
        center_y = player.rect.centery + \
            math.sin(radians) * settings.SABER_ORBIT_RADIUS

        self.rect.center = (center_x, center_y)
        self.x = self.rect.x
        self.y = self.rect.y

        # cooldowns de dano correm independente de colisao, para destravar no tempo certo
        for enemy_id in list(self._hit_cooldowns.keys()):
            self._hit_cooldowns[enemy_id] -= dt

            if self._hit_cooldowns[enemy_id] <= 0:
                del self._hit_cooldowns[enemy_id]

    def can_hit(self, enemy) -> bool:

        return id(enemy) not in self._hit_cooldowns

    def register_hit(self, enemy) -> None:

        self._hit_cooldowns[id(enemy)] = settings.SABER_HIT_COOLDOWN

    # ==================================================================
    # DESENHO
    # ==================================================================

    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:

        screen_rect = self.rect.copy()
        screen_rect.x -= camera_x
        screen_rect.y -= camera_y

        pygame.draw.circle(screen, (200, 220, 240),
                           screen_rect.center, self.width / 2)
