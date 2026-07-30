import pygame

from src import settings
from src.systems.door import Door
from src.entities.player import Player


class Room:
    """Representa uma sala navegavel do Modo 1 (Horde Interna): geometria,
    portas, obstaculos, inimigos vivos, e todo o estado de rejogabilidade
    (visitas, reentradas, cronometro de sobrevivencia, estatisticas e
    historico por visita)."""

    def __init__(self, x: int, y: int, width: int, height: int, room_id: int, wall: int = 20) -> None:

        # --- geometria basica ---
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.wall: int = wall
        self.room_id: int = room_id
        self.doors: list[Door] = []

        # tipo Obstacle, import evitado aqui p/ nao criar dependencia circular
        self.obstacles: list = []

        # tipo Enemy, import evitado aqui p/ nao criar dependencia circular
        self.enemies: list = []

        # --- rejogabilidade: contagem de visitas e ciclo de limpeza ---
        self.times_cleared: int = 0  # quantas vezes esta sala ja foi totalmente limpa
        # True quando a sala foi esvaziada neste ciclo, ate ser reaberta
        self.cleared: bool = False
        # tamanho da horda ao ser gerada, para exibir X/Y na HUD
        self.horde_total_enemies: int = 0

        # --- reentradas: limite de revisitas, regenera com o tempo ---
        self.max_reentries: int = settings.ROOM_MAX_REENTRIES
        self.reentries: int = self.max_reentries
        self.regen_interval: float = settings.ROOM_REGEN_INTERVAL
        self.last_regen_time: float = 0.0

        # --- cronometro de duracao da horda atual ---
        self.horde_start_time: float = 0.0
        self.horde_clear_time: float | None = None  # None enquanto a horda esta ativa

        # --- piso continuo de inimigos: sala mantem uma quantidade minima viva, reabastecendo sempre ---
        # survival_elapsed acumula via dt (nao time.time()), para pausar corretamente
        # durante a tela de escolha de upgrade - sem isso, o jogador podia "descontar"
        # tempo de sobrevivencia/onda so ficando parado na tela de escolha
        self.survival_elapsed: float = 0.0
        # segundos para "vencer" a sala
        self.survival_duration: float = settings.ROOM_SURVIVAL_DURATION
        # True quando o tempo esgota - para o reabastecimento, mas exige eliminar quem restou
        self.time_expired: bool = False

        # --- sistema de ondas: cada onda soma inimigos aos remanescentes, sem esperar limpar a atual -
        # (Sprint A do Bloco de Entidades de Chefes - so a mecanica de acumulo, sem chefes ainda) ---
        self.current_wave: int = 1  # onda atual desta visita, reinicia a cada spawn_horde()
        # countdown ate a PROXIMA onda ser somada
        self.wave_timer: float = settings.WAVE_DURATION

        # --- agenda de chefes: guarda (boss_type, indice) ja disparados nesta visita,
        # para cada ponto de settings.BOSS_SPAWN_SCHEDULE nascer uma unica vez -
        # reiniciado a cada spawn_horde() (nova visita/reentrada) ---
        self.boss_spawns_triggered: set = set()

        # --- mesmo controle, mas para o AVISO visual (dispara antes do spawn real) ---
        self.boss_warnings_triggered: set = set()

        # --- estatisticas desta sala: mortos e pontos gerados, por tipo de inimigo ---
        self.kills_by_type: dict = {}
        self.points_by_type: dict = {}

        # --- historico por visita: cada entrada e um registro de uma sessao concluida ---
        self.visit_history: list[dict] = []

    # ==================================================================
    # REENTRADAS (limite de revisitas por sala)
    # ==================================================================

    def has_reentries_left(self) -> bool:

        self.regen_reentries()
        return self.reentries > 0

    def consume_reentry(self) -> None:

        self.reentries -= 1
        self.last_regen_time = self._now()  # reinicia o cronometro a cada consumo

    def regen_reentries(self) -> None:

        if self.reentries >= self.max_reentries:
            return

        if self.last_regen_time == 0.0:
            return

        elapsed = self._now() - self.last_regen_time
        regenerated = int(elapsed // self.regen_interval)

        if regenerated > 0:
            self.reentries = min(
                self.max_reentries, self.reentries + regenerated)
            self.last_regen_time = self._now()

    def time_until_next_regen(self) -> float:

        # quanto tempo falta para a proxima reentrada regenerar, em segundos (0 se ja no maximo)
        if self.reentries >= self.max_reentries:
            return 0.0

        if self.last_regen_time == 0.0:
            return 0.0

        elapsed = self._now() - self.last_regen_time
        remaining = self.regen_interval - (elapsed % self.regen_interval)

        return remaining

    def _now(self) -> float:

        import time
        return time.time()

    # ==================================================================
    # LIMITES E GEOMETRIA
    # ==================================================================

    def get_bounds(self) -> tuple[int, int, int, int]:

        return (self.rect.left + self.wall,
                self.rect.top + self.wall,
                self.rect.right - self.wall,
                self.rect.bottom - self.wall,
                )

    # ==================================================================
    # PORTAS
    # ==================================================================

    def add_door(self, door: Door) -> None:

        self.doors.append(door)

    def get_doors(self) -> list[Door]:

        return self.doors

    def get_colliding_door(self, player: Player) -> Door | None:

        for door in self.doors:

            if door.collides(player):
                return door
        return None

    def get_door_by_id(self, door_id: int) -> Door | None:

        for door in self.doors:
            if door.id == door_id:
                return door

        return None

    # ==================================================================
    # OBSTACULOS
    # ==================================================================

    def add_obstacle(self, obstacle) -> None:

        self.obstacles.append(obstacle)

    def get_obstacles(self) -> list:

        return self.obstacles

    # ==================================================================
    # INIMIGOS
    # ==================================================================

    def add_enemy(self, enemy) -> None:

        self.enemies.append(enemy)

    def get_enemies(self) -> list:

        return self.enemies

    def remove_dead_enemies(self) -> None:

        self.enemies = [e for e in self.enemies if not e.is_dead]

    def remove_destroyed_obstacles(self) -> None:

        self.obstacles = [o for o in self.obstacles if not o.is_dead]

    def register_kill(self, enemy_type: str, points: float) -> None:

        self.kills_by_type[enemy_type] = self.kills_by_type.get(
            enemy_type, 0) + 1
        self.points_by_type[enemy_type] = self.points_by_type.get(
            enemy_type, 0.0) + points

    # ==================================================================
    # DESENHO
    # ==================================================================

    def draw_floor_grid(self, screen: pygame.Surface, rl: float, rt: float) -> None:

        # grade sutil no piso, para dar referencia visual de movimento
        grid_size = 64
        # levemente mais claro que o piso (55, 60, 70)
        grid_color = (60, 66, 78)

        # linhas verticais
        x = self.wall
        while x < self.rect.width - self.wall:
            start = (rl + x, rt + self.wall)
            end = (rl + x, rt + self.rect.height - self.wall)
            pygame.draw.line(screen, grid_color, start, end, 1)
            x += grid_size

        # linhas horizontais
        y = self.wall
        while y < self.rect.height - self.wall:
            start = (rl + self.wall, rt + y)
            end = (rl + self.rect.width - self.wall, rt + y)
            pygame.draw.line(screen, grid_color, start, end, 1)
            y += grid_size

    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:

        # todas as coordenadas da sala sao deslocadas pela camera antes de desenhar
        rl, rt = self.rect.left - camera_x, self.rect.top - camera_y

        # Piso
        pygame.draw.rect(
            screen, (55, 60, 70), (rl, rt, self.rect.width, self.rect.height),)

        self.draw_floor_grid(screen, rl, rt)

        # Parede Superior
        pygame.draw.rect(screen, (95, 100, 115),
                         (rl, rt, self.rect.width, self.wall),)

        # Parede Inferior
        pygame.draw.rect(screen, (95, 100, 115), (rl,
                         rt + self.rect.height - self.wall, self.rect.width, self.wall),)

        # Parede Esquerda
        pygame.draw.rect(screen, (95, 100, 115),
                         (rl, rt, self.wall, self.rect.height),)

        # Parede Direita
        pygame.draw.rect(screen, (95, 100, 115), (rl + self.rect.width -
                         self.wall, rt, self.wall, self.rect.height),)

        # Contorno
        pygame.draw.rect(screen, (145, 150, 165),
                         (rl, rt, self.rect.width, self.rect.height), width=2,)

        # texto de sala/visitas vive na HUD fixa (GameScene.draw_ui), Sprint 016

        for obstacle in self.obstacles:
            obstacle.draw(screen, camera_x, camera_y)

        for door in self.doors:
            door.draw(screen, camera_x, camera_y)

        for enemy in self.enemies:
            enemy.draw(screen, camera_x, camera_y)
