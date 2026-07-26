import time
import random

import pygame

from src.scenes.scene import Scene
from src.systems.entity_manager import EntityManager
from src.entities.player import Player
from src.systems.room import Room
from src.systems.door import Door, TOP, BOTTOM, LEFT, RIGHT
from src import settings


class GameScene(Scene):

    # ==================================================================
    # TABELAS DE CONFIGURACAO DE CLASSE
    # ==================================================================

    # dimensoes de cada sala: Area de Carga (grande), Corredor (longo e estreito), Engenharia
    ROOM_SIZES = {
        1: (1280, 960),
        2: (300, 1400),
        3: (900, 700),
    }

    # inimigos nao nascem mais perto que isso de qualquer porta da sala
    SAFE_DISTANCE_FROM_DOOR = settings.SAFE_SPAWN_DISTANCE

    def __init__(self) -> None:

        # --- entidades e listas de objetos temporarios ---
        self.entity_manager: EntityManager = EntityManager()

        from src.entities.projectile import Projectile
        self.projectiles: list[Projectile] = []

        from src.entities.floating_text import FloatingText
        self.floating_texts: list[FloatingText] = []

        from src.entities.gem import Gem
        self.gems: list[Gem] = []

        self.rooms: dict[int, Room] = {}

        # --- dados de portas: cada porta conhece sua sala, posicao e porta destino ---
        self.door_data = {
            1: {
                "room": 1,
                "x": 700,
                "y": 1000,
                "width": 40,
                "height": 20,
                "side": BOTTOM,
                "target": 2,
            },
            2: {
                "room": 2,
                "x": 210,
                "y": 60,
                "width": 40,
                "height": 20,
                "side": TOP,
                "target": 1,
            },
            3: {
                "room": 2,
                "x": 210,
                "y": 1440,
                "width": 40,
                "height": 20,
                "side": BOTTOM,
                "target": 4,
            },
            4: {
                "room": 3,
                "x": 510,
                "y": 60,
                "width": 40,
                "height": 20,
                "side": TOP,
                "target": 3,
            },
        }

        # --- dados de sala: cada sala conhece seu nivel e quais portas possui ---
        self.room_data = {
            1: {
                "level": 1,
                "doors": [1],
                "spawn": (704, 524),
            },
            2: {
                "level": 2,
                "doors": [2, 3],
            },
            3: {
                "level": 2,
                "doors": [4],
            },
        }

        # --- obstaculos fixos por sala: posicionados manualmente (ate o Nivel 11, quando vira automatico) ---
        self.obstacle_data = {
            1: [
                {"x": 400, "y": 300, "width": 80, "height": 80},
                {"x": 900, "y": 500, "width": 60, "height": 120},
            ],
        }

        # --- sala inicial e jogador ---
        self.current_room_id: int = 1
        self.room: Room = self.create_room(self.current_room_id)

        spawn_x, spawn_y = self.room_data[self.current_room_id]["spawn"]
        self.player: Player = Player(spawn_x, spawn_y)
        self.player.room = self.room
        self.entity_manager.add(self.player)

        # --- estado auxiliar de log e camera ---
        self.last_state: str | None = None
        self.camera_x: float = 0.0
        self.camera_y: float = 0.0

    # ==================================================================
    # CRIACAO E CONFIGURACAO DE SALAS
    # ==================================================================

    def spawn_horde(self, room: Room) -> None:
        """Preenche a sala com o piso minimo de inimigos e inicia o
        cronometro de sobrevivencia. A sala mantem uma quantidade minima
        de inimigos vivos o tempo todo, reabastecida continuamente."""

        room.survival_start_time = time.time()
        room.time_expired = False

        # zera estatisticas da visita anterior - o historico ja foi preservado em visit_history
        room.kills_by_type = {}
        room.points_by_type = {}

        enemy_count = settings.HORDE_BASE_ENEMIES
        room.horde_total_enemies = enemy_count

        self._spawn_wave_enemies(room, enemy_count)

    def _spawn_wave_enemies(self, room: Room, enemy_count: int) -> None:
        """Sorteia posicoes nas bordas da sala para uma leva de inimigos,
        respeitando distancia minima das portas. O tipo de cada inimigo e
        escolhido individualmente, com chance de ser forte crescendo ao
        longo do tempo de permanencia na sala (ver _pick_enemy_type)."""

        from src.entities.enemy import Enemy

        left, top, right, bottom = room.get_bounds()

        door_positions = [door.rect.center for door in room.get_doors()]

        for _ in range(enemy_count):

            # tenta ate 20 vezes achar uma posicao longe o suficiente das portas
            for _attempt in range(20):

                edge = random.randint(0, 3)

                if edge == 0:
                    x, y = random.randint(left, right), top
                elif edge == 1:
                    x, y = random.randint(left, right), bottom
                elif edge == 2:
                    x, y = left, random.randint(top, bottom)
                else:
                    x, y = right, random.randint(top, bottom)

                far_enough = all(
                    pygame.Vector2(
                        x - dx, y - dy).length() >= self.SAFE_DISTANCE_FROM_DOOR
                    for dx, dy in door_positions
                )

                if far_enough or not door_positions:
                    break

            enemy_type = self._pick_enemy_type(room)
            room.add_enemy(Enemy(x, y, enemy_type=enemy_type))

    def _pick_enemy_type(self, room: Room) -> str:
        """Escolhe o tipo do inimigo individualmente: a chance de ser
        'strong' cresce linearmente com o tempo de permanencia na sala,
        ate um teto configurado."""

        elapsed = time.time() - room.survival_start_time

        progress = min(1.0, elapsed / settings.STRONG_ENEMY_RAMP_TIME)
        chance = progress * settings.STRONG_ENEMY_MAX_CHANCE

        return "strong" if random.random() < chance else "weak"

    def _spawn_destructible_obstacles(self, room: Room) -> None:
        """Gera obstaculos destrutiveis em posicoes aleatorias, evitando
        sobrepor obstaculos fixos ja existentes e a area central da sala
        (onde o jogador normalmente aparece/atravessa)."""

        from src.entities.obstacle import Obstacle

        left, top, right, bottom = room.get_bounds()
        size = settings.DESTRUCTIBLE_OBSTACLE_SIZE

        existing_rects = [o.rect for o in room.get_obstacles()]

        avoid_center = pygame.Vector2(room.rect.centerx, room.rect.centery)
        avoid_radius = 100

        for _ in range(settings.DESTRUCTIBLE_OBSTACLES_PER_ROOM):

            for _attempt in range(20):

                x = random.randint(int(left), int(right - size))
                y = random.randint(int(top), int(bottom - size))

                candidate_rect = pygame.Rect(x, y, size, size)

                too_close_to_center = (
                    pygame.Vector2(candidate_rect.centerx,
                                   candidate_rect.centery)
                    .distance_to(avoid_center) < avoid_radius
                )

                overlaps_existing = any(
                    candidate_rect.colliderect(r) for r in existing_rects)

                if not too_close_to_center and not overlaps_existing:
                    break

            obstacle = Obstacle(
                x=x, y=y, width=size, height=size,
                destructible=True, hp=settings.DESTRUCTIBLE_OBSTACLE_HP)

            room.add_obstacle(obstacle)
            existing_rects.append(obstacle.rect)

    def create_room(self, room_id: int) -> Room:
        """Retorna a sala do cache, gerando uma nova horda se ela ja tiver sido
        limpa (respeitando reentradas), ou cria a sala do zero na primeira visita."""

        if room_id in self.rooms:
            room = self.rooms[room_id]

            # reentrando em sala ja limpa: consome reentrada, gera nova horda, tranca portas
            if room.cleared and not room.get_enemies():
                room.consume_reentry()

                self.spawn_horde(room)

                for door in room.get_doors():
                    door.lock()

                room.cleared = False

            return room

        width, height = self.ROOM_SIZES[room_id]
        room = Room(80, 60, width, height, room_id=room_id)

        self.configure_room(room, room_id)

        self.rooms[room_id] = room

        return room

    def configure_room(self, room: Room, room_id: int) -> None:
        """Monta as portas da sala a partir de room_data/door_data,
        cria os obstaculos fixos (obstacle_data) e destrutiveis
        (aleatorios), e gera a primeira horda (trancando as portas
        se houver inimigos)."""

        room_info = self.room_data[room_id]

        for door_id in room_info["doors"]:

            door_info = self.door_data[door_id]

            room.add_door(
                Door(
                    id=door_id,
                    x=door_info["x"],
                    y=door_info["y"],
                    width=door_info["width"],
                    height=door_info["height"],
                    side=door_info["side"],
                    target_door=door_info["target"]
                ))

        # cria os obstaculos fixos desta sala, se houver algum definido
        from src.entities.obstacle import Obstacle

        for obstacle_info in self.obstacle_data.get(room_id, []):
            room.add_obstacle(
                Obstacle(
                    x=obstacle_info["x"],
                    y=obstacle_info["y"],
                    width=obstacle_info["width"],
                    height=obstacle_info["height"],
                ))

        # gera obstaculos destrutiveis aleatorios, evitando sobrepor os fixos
        self._spawn_destructible_obstacles(room)

        self.spawn_horde(room)

        # tranca todas as portas da sala se ela tiver inimigos - destranca quando a sala for limpa
        if room.get_enemies():
            for door in room.get_doors():
                door.lock()

    # ==================================================================
    # COMBATE
    # ==================================================================

    def spawn_damage_text(self, x: float, y: float, amount: int) -> None:
        """Cria um texto flutuante de dano na posicao informada."""

        from src.entities.floating_text import FloatingText
        self.floating_texts.append(
            FloatingText(x, y - 20, f"-{amount}"))

    def find_closest_enemy(self, enemies: list):
        """Retorna o inimigo vivo mais proximo do player, dentro do raio de
        percepcao (player.range_radius) e com linha de visao livre (sem
        obstaculo no caminho), ou None se nenhum atender aos dois criterios."""

        closest = None
        closest_distance = None

        for enemy in enemies:
            distance = pygame.Vector2(
                enemy.x - self.player.x, enemy.y - self.player.y).length()

            if distance > self.player.range_radius:
                continue  # fora do alcance de percepcao, ignora

            if not self._has_line_of_sight(self.player.rect.center, enemy.rect.center):
                continue  # obstaculo bloqueia a visao, "cego" para este inimigo

            if closest_distance is None or distance < closest_distance:
                closest = enemy
                closest_distance = distance

        return closest

    def _has_line_of_sight(self, start: tuple, end: tuple) -> bool:
        """Verifica se a linha reta entre dois pontos e bloqueada por
        algum obstaculo da sala atual, usando o algoritmo de clipping
        de linha do proprio pygame.Rect (clipline)."""

        for obstacle in self.room.get_obstacles():
            if obstacle.rect.clipline(start, end):
                return False  # a linha cruza este obstaculo

        return True

    # ==================================================================
    # LOOP PRINCIPAL
    # ==================================================================

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:

        # --- entidades e camera ---
        self.entity_manager.update(dt)
        self.update_camera()

        # --- limpeza de inimigos mortos e obstaculos destruidos ---
        self.room.remove_dead_enemies()
        self.room.remove_destroyed_obstacles()

        # --- atualiza obstaculos (cooldown de corrosao e encolhimento visual) ---
        for obstacle in self.room.get_obstacles():
            obstacle.update(dt)

        # --- verifica se o jogo terminou de vez (sem vidas restantes) ---
        game_over = self.player.is_dead and not self.player.has_lives_left()

        # --- piso continuo: reabastece inimigos ate manter o minimo vivo ---
        current_count = len(self.room.get_enemies())
        missing = self.room.horde_total_enemies - current_count

        if (missing > 0 and not self.room.cleared
                and not self.room.time_expired and not game_over):
            self._spawn_wave_enemies(self.room, missing)

        # --- condicao de vitoria: sobreviver por tempo determinado ---
        if game_over:
            survival_elapsed = self.room.horde_clear_time or 0.0
        else:
            survival_elapsed = time.time() - self.room.survival_start_time

        # ao esgotar o tempo, para de reabastecer - so destranca quando nao houver mais inimigos vivos
        if not game_over and survival_elapsed >= self.room.survival_duration:
            self.room.time_expired = True

        if (self.room.time_expired and not self.room.get_enemies()
                and not self.room.cleared):

            for door in self.room.get_doors():
                door.unlock()

            self.room.cleared = True
            self.room.times_cleared += 1
            self.room.horde_clear_time = survival_elapsed

            # registra esta visita no historico, antes que as estatisticas da sala sejam zeradas na proxima
            self.room.visit_history.append({
                "visit_number": self.room.times_cleared,
                "clear_time": survival_elapsed,
                "kills_by_type": dict(self.room.kills_by_type),
                "points_by_type": dict(self.room.points_by_type),
                "total_points": sum(self.room.points_by_type.values()),
            })

        enemies = self.room.get_enemies()

        # --- disparo automatico do player ---
        if self.player.ready_to_shoot() and enemies:
            target = self.find_closest_enemy(enemies)

            if target is not None:

                direction = pygame.Vector2(
                    target.x - self.player.x, target.y - self.player.y)

                if direction.length_squared() > 0:
                    direction = direction.normalize()

                    from src.entities.projectile import Projectile
                    self.projectiles.append(Projectile(
                        self.player.x, self.player.y, direction,
                        max_range=self.player.range_radius,
                        damage=self.player.shoot_damage))

                    self.player.confirm_shot()

        # --- projeteis: movimento, colisao com obstaculos e com inimigos ---
        for projectile in self.projectiles:
            projectile.update(dt)

            # todo obstaculo bloqueia o projetil do player, independente de ser destrutivel
            # (destrutiveis so sao corroidos por inimigos, nao pelo tiro do player)
            for obstacle in self.room.get_obstacles():
                if not obstacle.is_dead and projectile.rect.colliderect(obstacle.rect):
                    projectile.is_dead = True
                    break

            if projectile.is_dead:
                continue  # ja bloqueado pelo obstaculo, nao verifica inimigos

            for enemy in enemies:
                if not enemy.is_dead and projectile.rect.colliderect(enemy.rect):
                    enemy.take_damage(projectile.damage)
                    projectile.register_hit()  # decrementa pierce; morre quando chega a 0

                    self.spawn_damage_text(
                        enemy.x, enemy.y, projectile.damage)

                    if enemy.is_dead:
                        self.player.register_kill(
                            enemy.enemy_type, enemy.drop_value)
                        self.room.register_kill(
                            enemy.enemy_type, enemy.drop_value)

                        from src.entities.gem import Gem
                        self.gems.append(
                            Gem(enemy.x, enemy.y, enemy.drop_value))
                    break

        left, top, right, bottom = self.room.get_bounds()

        for projectile in self.projectiles:
            if (projectile.x < left or projectile.x > right
                    or projectile.y < top or projectile.y > bottom):
                projectile.is_dead = True  # saiu da area jogavel, marca para remocao

        self.projectiles = [p for p in self.projectiles if not p.is_dead]

        # --- textos flutuantes de dano ---
        for text in self.floating_texts:
            text.update(dt)

        self.floating_texts = [t for t in self.floating_texts if not t.is_dead]

        # --- gemas: inicia o arrasto ao entrar no raio (pickup normal OU ima), move, coleta ao chegar perto o suficiente ---
        magnet_radius = self.player.get_passive_value("magnet")
        pull_trigger_radius = max(settings.GEM_PICKUP_RADIUS, magnet_radius)

        for gem in self.gems:
            if gem.is_dead:
                continue

            distance = pygame.Vector2(
                gem.rect.centerx - self.player.rect.centerx,
                gem.rect.centery - self.player.rect.centery
            ).length()

            if not gem.being_pulled and distance <= pull_trigger_radius:
                gem.start_pull()

            if gem.being_pulled:
                gem.update_pull(
                    dt, self.player.rect.centerx, self.player.rect.centery,
                    settings.GEM_PULL_ACCELERATION, settings.GEM_PULL_MAX_SPEED)

                if distance <= settings.GEM_COLLECT_DISTANCE:
                    self.player.add_drop_point(gem.value)
                    gem.is_dead = True

        self.gems = [g for g in self.gems if not g.is_dead]

        # --- inimigos: movimento e colisao com o player ---
        if not self.player.is_dead:  # inimigos param de agir assim que o jogador morre

            room_bounds = self.room.get_bounds()
            room_obstacles = self.room.get_obstacles()

            for enemy in enemies:
                enemy.update(dt, self.player.x, self.player.y,
                             enemies, room_bounds, room_obstacles)

            # inimigo corroi obstaculo destrutivel por proximidade (nao apenas sobreposicao exata)
            # usa uma area "inflada" para deteccao, ja que o bloqueio de movimento impede sobreposicao real
            attack_reach = 6  # pixels de folga alem da borda do obstaculo, para contar como "encostado"

            for enemy in enemies:
                for obstacle in room_obstacles:
                    if obstacle.destructible and not obstacle.is_dead:
                        inflated_rect = obstacle.rect.inflate(
                            attack_reach * 2, attack_reach * 2)

                        if enemy.rect.colliderect(inflated_rect):
                            obstacle.take_damage(
                                settings.ENEMY_OBSTACLE_DAMAGE)

            for enemy in enemies:
                if self.player.rect.colliderect(enemy.rect):
                    self.player.take_damage(enemy.damage)
                    self.player.apply_knockback(enemy.x, enemy.y)

                    self.spawn_damage_text(
                        self.player.x, self.player.y, enemy.damage)

                    if self.player.is_dead:

                        self.player.consume_life()

                        if self.player.has_lives_left():
                            print(
                                f"Continuando... Vidas restantes: {self.player.lives}")
                            self.player.revive()
                        else:
                            print("GAME OVER DEFINITIVO - sem vidas restantes")

                    break

        # --- transicao de sala ---
        if self.player.consume_room_change():

            target_door_id = self.player.current_door.target_door

            self.current_room_id = self.door_data[target_door_id]["room"]

            self.room = self.create_room(self.current_room_id)

            self.player.room = self.room

            target_door = self.room.get_door_by_id(target_door_id)

            spawn_x, spawn_y = target_door.get_spawn_position()

            self.player.x = spawn_x - self.player.width / 2
            self.player.y = spawn_y - self.player.height / 2

            self.player.rect.center = (spawn_x, spawn_y)

            return

        # --- deteccao e abertura de portas ---

        # atualiza o feedback visual de bloqueio de reentrada, para toda porta da sala atual
        for current_door in self.room.get_doors():
            dest_room_id = self.door_data[current_door.target_door]["room"]
            dest_room = self.rooms.get(dest_room_id)

            current_door.reentry_blocked = (
                dest_room is not None
                and dest_room.cleared
                and not dest_room.get_enemies()
                and not dest_room.has_reentries_left()
            )

        door: Door = self.room.get_colliding_door(self.player)

        for current_door in self.room.get_doors():
            current_door.close()

        if self.player.state != self.last_state:
            print(f"State -> {self.player.state}")
            self.last_state = self.player.state

        if door:

            door.open()

            if self.player.current_door != door:
                self.player.current_door = door

                if self.player.state == "walking":

                    target_room_id = self.door_data[door.target_door]["room"]
                    target_room = self.rooms.get(target_room_id)

                    # reentrada: sala ja visitada, ja vencida, e sem inimigos no momento
                    is_reentry = (target_room is not None
                                  and target_room.cleared
                                  and not target_room.get_enemies())

                    if is_reentry and not target_room.has_reentries_left():
                        # feedback ja visivel na cor roxa da porta (reentry_blocked)
                        pass
                    else:
                        alignment_point = door.get_alignment_point(
                            self.player.x, self.player.y, self.player.width, self.player.height)
                        entry_point = door.get_entry_target(
                            self.player.width, self.player.height)

                        self.player.start_door_sequence(
                            [alignment_point, entry_point], door.get_thickness())

                        self.player.state = "entering_door"

                        print(f"Door -> {door.side} -> Room {target_room_id}")

        else:

            if self.player.state == "walking":
                self.player.current_door = None

    def update_camera(self) -> None:
        """Centraliza a sala se ela couber na janela; segue o player, com
        limites, se a sala for maior que a janela em qualquer eixo."""

        room_rect = self.room.rect

        if room_rect.width <= settings.WINDOW_WIDTH:
            self.camera_x = room_rect.centerx - settings.WINDOW_WIDTH / 2
        else:
            target_x = self.player.rect.centerx - settings.WINDOW_WIDTH / 2
            max_camera_x = room_rect.right - settings.WINDOW_WIDTH
            self.camera_x = max(room_rect.left, min(target_x, max_camera_x))

        if room_rect.height <= settings.WINDOW_HEIGHT:
            self.camera_y = room_rect.centery - settings.WINDOW_HEIGHT / 2
        else:
            target_y = self.player.rect.centery - settings.WINDOW_HEIGHT / 2
            max_camera_y = room_rect.bottom - settings.WINDOW_HEIGHT
            self.camera_y = max(room_rect.top, min(target_y, max_camera_y))

    # ==================================================================
    # DESENHO
    # ==================================================================

    def draw(self, screen: pygame.Surface) -> None:
        self.draw_background(screen)
        self.draw_world(screen)
        self.draw_ui(screen)

    def draw_background(self, screen: pygame.Surface) -> None:

        screen.fill((18, 20, 30))

        self.room.draw(screen, self.camera_x, self.camera_y)

    def draw_world(self, screen: pygame.Surface) -> None:

        self.entity_manager.draw(screen, self.camera_x, self.camera_y)

        for projectile in self.projectiles:
            projectile.draw(screen, self.camera_x, self.camera_y)

        for gem in self.gems:
            gem.draw(screen, self.camera_x, self.camera_y)

        for text in self.floating_texts:
            text.draw(screen, self.camera_x, self.camera_y)

    def draw_ui(self, screen: pygame.Surface) -> None:

        # --- elementos essenciais, sempre visiveis ---
        self.draw_hp_bar(screen)
        self.draw_progress_bar(screen)
        self.draw_room_and_lives(screen)

        # --- painel de debug, compacto e translucido ---
        self.draw_debug_panel(screen)

    def draw_hp_bar(self, screen: pygame.Surface) -> None:

        bar_x, bar_y = 20, 20
        bar_width, bar_height = 200, 24

        hp_ratio = self.player.hp / self.player.max_hp

        pygame.draw.rect(screen, (80, 30, 30),
                         (bar_x, bar_y, bar_width, bar_height))

        pygame.draw.rect(screen, (60, 180, 90),
                         (bar_x, bar_y, bar_width * hp_ratio, bar_height))

        pygame.draw.rect(screen, (255, 255, 255),
                         (bar_x, bar_y, bar_width, bar_height), width=2)

        font = pygame.font.Font(None, 24)
        text = font.render(
            f"HP: {self.player.hp}/{self.player.max_hp}", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (bar_x + bar_width / 2, bar_y + bar_height / 2)
        screen.blit(text, text_rect)

    def draw_progress_bar(self, screen: pygame.Surface) -> None:

        bar_x, bar_y = 20, 46
        bar_width, bar_height = 200, 10

        ratio = self.player.drop_points / self.player.points_to_upgrade
        ratio = min(1.0, ratio)

        pygame.draw.rect(screen, (50, 30, 70),
                         (bar_x, bar_y, bar_width, bar_height))

        pygame.draw.rect(screen, (200, 170, 60),
                         (bar_x, bar_y, bar_width * ratio, bar_height))

        pygame.draw.rect(screen, (255, 255, 255),
                         (bar_x, bar_y, bar_width, bar_height), width=1)

        font = pygame.font.Font(None, 22)
        text = font.render(f"Level {self.player.level}", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.midleft = (bar_x + bar_width + 10, bar_y + bar_height / 2)
        screen.blit(text, text_rect)

    def draw_room_and_lives(self, screen: pygame.Surface) -> None:

        font = pygame.font.Font(None, 26)
        text = font.render(
            f"Room {self.room.room_id}  |  Vidas: {self.player.lives}/{self.player.max_lives}",
            True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.topleft = (20, 62)
        screen.blit(text, text_rect)

    # ==================================================================
    # PAINEL DE DEBUG (tela de desenvolvimento, sera revisado depois)
    # ==================================================================

    def draw_debug_panel(self, screen: pygame.Surface) -> None:

        font = pygame.font.Font(None, 20)
        line_height = 18
        padding = 8

        lines = self._build_debug_lines()

        panel_width = 260
        panel_height = padding * 2 + line_height * len(lines)
        panel_x, panel_y = 20, 92

        panel_surface = pygame.Surface(
            (panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((20, 20, 30, 140))
        screen.blit(panel_surface, (panel_x, panel_y))

        y = panel_y + padding
        for line in lines:
            text = font.render(line, True, (220, 220, 220))
            screen.blit(text, (panel_x + padding, y))
            y += line_height

    def _build_debug_lines(self) -> list[str]:

        self.room.regen_reentries()

        lines = []

        lines.append(
            f"Visitas: {self.room.times_cleared}  |  "
            f"Reentradas: {self.room.reentries}/{self.room.max_reentries}")

        lines.append(self._build_survival_line())
        lines.append(self._build_enemy_counter_line())
        lines.append(self._build_progress_line())
        lines.append(self._build_magnet_line())

        lines.append("")
        lines.append("Estatisticas totais (mortos / pontos):")
        lines.extend(self._build_kill_stat_lines(
            self.player.kills_by_type, self.player.points_by_type))

        lines.append("")
        lines.append("Salas:")

        for room_id in sorted(self.rooms.keys()):
            room = self.rooms[room_id]
            room.regen_reentries()

            timer_text = (f"{room.time_until_next_regen():.0f}s"
                          if room.reentries < room.max_reentries else "cheio")

            lines.append(
                f"  Room {room_id}: {room.reentries}/{room.max_reentries} ({timer_text})")

            for enemy_type in sorted(room.kills_by_type.keys()):
                kills = room.kills_by_type[enemy_type]
                points = room.points_by_type[enemy_type]
                lines.append(
                    f"    {enemy_type}: {kills} mortos, {points:.1f} pts")

            for entry in reversed(room.visit_history):
                lines.append(
                    f"    Visita {entry['visit_number']}: "
                    f"{entry['clear_time']:.1f}s, {entry['total_points']:.1f} pts")

                for enemy_type in sorted(entry['kills_by_type'].keys()):
                    kills = entry['kills_by_type'][enemy_type]
                    lines.append(f"      {enemy_type}: {kills}")

        return lines

    def _build_survival_line(self) -> str:

        if self.room.cleared:
            return f"Sala vencida em: {self.room.horde_clear_time:.1f}s"

        if self.player.is_dead and not self.player.has_lives_left():
            return "Sobrevivendo: -- (GAME OVER)"

        elapsed = time.time() - self.room.survival_start_time
        remaining = max(0.0, self.room.survival_duration - elapsed)

        return f"Sobrevivendo: {elapsed:.1f}s (faltam {remaining:.1f}s)"

    def _build_enemy_counter_line(self) -> str:

        total = self.room.horde_total_enemies

        if total == 0:
            return "Inimigos: --"

        current = len(self.room.get_enemies())

        return f"Inimigos vivos: {current} (piso: {total})"

    def _build_progress_line(self) -> str:

        return f"Dano do tiro: {self.player.shoot_damage}"

    def _build_magnet_line(self) -> str:

        level = self.player.passive_levels["magnet"]
        radius = self.player.get_passive_value("magnet")

        return f"Ima: nivel {level} (raio {radius:.0f}px)"

    def _build_kill_stat_lines(self, kills_by_type: dict, points_by_type: dict) -> list[str]:

        lines = []

        for enemy_type in sorted(kills_by_type.keys()):
            kills = kills_by_type[enemy_type]
            points = points_by_type[enemy_type]
            lines.append(f"  {enemy_type}: {kills} mortos, {points:.1f} pts")

        total_kills = sum(kills_by_type.values())
        total_points = sum(points_by_type.values())
        lines.append(f"  Total: {total_kills} mortos, {total_points:.1f} pts")

        return lines
