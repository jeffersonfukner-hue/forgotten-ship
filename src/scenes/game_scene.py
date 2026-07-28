import time
import random
import math

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

        from src.entities.saber import Saber
        self.sabers: list[Saber] = []

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

        # --- escolha de upgrade: None = jogo roda normal; lista = pausado, aguardando escolha ---
        self.upgrade_choices: list[str] | None = None

        # --- sifao de energia: feixe visual instantaneo, (inicio, fim, tempo_restante) ou None ---
        self.siphon_beam: tuple | None = None

        # --- painel de debug: TAB expande/recolhe o historico detalhado (estatisticas, salas) ---
        self.debug_expanded: bool = False

        # --- tempo de jogo: acumula desde o inicio da sessao, nunca reseta entre salas ---
        self.session_time: float = 0.0

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
        """Cria um texto flutuante de dano (vermelho) na posicao informada."""

        from src.entities.floating_text import FloatingText
        self.floating_texts.append(
            FloatingText(x, y - 20, f"-{amount}"))

    def spawn_heal_text(self, x: float, y: float, amount: int) -> None:
        """Cria um texto flutuante de cura (verde) na posicao informada."""

        from src.entities.floating_text import FloatingText
        self.floating_texts.append(
            FloatingText(x, y - 20, f"+{amount}", color=(100, 220, 120)))

    def spawn_block_text(self, x: float, y: float) -> None:
        """Cria um texto flutuante de bloqueio total (azul) na posicao informada."""

        from src.entities.floating_text import FloatingText
        self.floating_texts.append(
            FloatingText(x, y - 20, "Bloqueado!", color=(120, 180, 240)))

    def get_enemies_by_distance(self, enemies: list) -> list:
        """Retorna os inimigos vivos dentro do raio de percepcao e com linha
        de visao livre, ordenados do mais proximo ao mais distante do
        player. Base para qualquer arma que precise mirar o Nº mais
        proximo (tiro principal usa o indice 0, Sifao usa o indice 1,
        armas futuras podem consumir indices seguintes)."""

        in_range = []

        for enemy in enemies:
            distance = pygame.Vector2(
                enemy.x - self.player.x, enemy.y - self.player.y).length()

            if distance > self.player.range_radius:
                continue  # fora do alcance de percepcao, ignora

            if not self._has_line_of_sight(self.player.rect.center, enemy.rect.center):
                continue  # obstaculo bloqueia a visao, "cego" para este inimigo

            in_range.append((distance, enemy))

        in_range.sort(key=lambda pair: pair[0])

        return [enemy for _distance, enemy in in_range]

    def find_closest_enemy(self, enemies: list):
        """Retorna o inimigo vivo mais proximo (mantido para compatibilidade
        com o disparo automatico principal) - equivale ao indice 0 de
        get_enemies_by_distance()."""

        ordered = self.get_enemies_by_distance(enemies)

        return ordered[0] if ordered else None

    def _get_quadrant(self, dx: float, dy: float) -> str:
        """Classifica um vetor (delta ate o alvo) em um dos 4 quadrantes
        fixos do mundo, cada um cobrindo 90 graus: direita (a fatia que
        nunca tem upgrade proprio, sempre reservada a Frente), baixo,
        esquerda (Tras) e cima."""

        angle = math.degrees(math.atan2(dy, dx))

        if -45 <= angle < 45:
            return "direita"
        if 45 <= angle < 135:
            return "baixo"
        if angle >= 135 or angle < -135:
            return "esquerda"
        return "cima"

    def _create_projectiles(self, shots: list) -> None:
        """Cria os projeteis para uma lista de disparos (direction+offset),
        aplicando velocidade e penetracao vindas dos upgrades do Tiro."""

        from src.entities.projectile import Projectile

        projectile_speed = self.player.get_passive_value("tiro_velocidade")
        pierce = int(self.player.get_passive_value("tiro_penetracao"))

        for shot in shots:
            self.projectiles.append(Projectile(
                self.player.x +
                shot["offset"].x, self.player.y + shot["offset"].y,
                shot["direction"], max_range=self.player.range_radius,
                damage=self.player.shoot_damage, speed=projectile_speed, pierce=pierce))

    def _has_line_of_sight(self, start: tuple, end: tuple) -> bool:
        """Verifica se a linha reta entre dois pontos e bloqueada por
        algum obstaculo da sala atual, usando o algoritmo de clipping
        de linha do proprio pygame.Rect (clipline)."""

        for obstacle in self.room.get_obstacles():
            if obstacle.rect.clipline(start, end):
                return False  # a linha cruza este obstaculo

        return True

    def sync_sabers(self) -> None:
        """Recria as instancias de Saber sempre que a quantidade muda, para
        que os angulos fiquem sempre uniformemente espacados entre si
        (2 laminas = lados opostos, 3 laminas = triangulo, etc.) - nao
        preserva instancias antigas, ja que a redistribuicao de angulo
        exige recalcular todas, nao so adicionar a nova."""

        from src.entities.saber import Saber

        target_count = int(self.player.get_passive_value("sabre_quantidade"))

        if target_count == len(self.sabers):
            return  # quantidade nao mudou, nada a fazer

        # preserva a fase de rotacao atual (angulo da primeira lamina existente),
        # para a lamina nao "pular" visualmente ao ganhar uma nova irma
        base_angle = self.sabers[0].angle if self.sabers else 0

        self.sabers = [
            Saber((base_angle + (360 / target_count) * i) % 360)
            for i in range(target_count)
        ]
    # ==================================================================
    # LOOP PRINCIPAL
    # ==================================================================

    def handle_event(self, event: pygame.event.Event) -> None:

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_TAB:
            self.debug_expanded = not self.debug_expanded
            return

        if self.upgrade_choices is None:
            return  # teclas 1/2/3 so processam quando a tela de escolha esta ativa

        key_to_index = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}

        index = key_to_index.get(event.key)

        if index is not None and index < len(self.upgrade_choices):
            chosen_key = self.upgrade_choices[index]
            self.player.apply_upgrade(chosen_key)
            self.upgrade_choices = None

    def update(self, dt: float) -> None:

        self.session_time += dt

        # ao detectar level up pendente, sorteia as opcoes e pausa o jogo ate a escolha
        if self.player.level_up_pending and self.upgrade_choices is None:
            self.upgrade_choices = self.player.choose_random_upgrades()
            self.player.level_up_pending = False

        if self.upgrade_choices is not None:
            return  # jogo totalmente pausado enquanto aguarda a escolha do jogador

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

        # --- rajada pendente: dispara a proxima repeticao, sem iniciar um novo ciclo de mira ---
        if self.player.has_pending_burst():
            if self.player.burst_timer <= 0:
                shots = self.player.pop_burst_shots()
                self._create_projectiles(shots)

                if self.player.has_pending_burst():
                    self.player.burst_timer = settings.BURST_SHOT_DELAY
                else:
                    self.player.confirm_shot()

        # --- disparo automatico do player (1 ou mais projeteis, conforme Tiro Multiplo) ---
        elif self.player.ready_to_shoot() and enemies:

            quadrant_level = self.player.passive_levels["tiro_quadrantes"]

            if quadrant_level > 0:
                # --- Quadrantes: cada direcao liberada mira seu proprio alvo mais proximo,
                # dentro da sua fatia de 90 graus; a Frente cobre o que sobrar ---
                ordered_enemies = self.get_enemies_by_distance(enemies)

                claimed_quadrants = []
                if quadrant_level >= 1:
                    claimed_quadrants.append("esquerda")
                if quadrant_level >= 2:
                    claimed_quadrants.append("cima")
                if quadrant_level >= 3:
                    claimed_quadrants.append("baixo")

                directions = []

                for quadrant in claimed_quadrants:
                    dedicated_target = next(
                        (e for e in ordered_enemies
                         if self._get_quadrant(e.x - self.player.x, e.y - self.player.y) == quadrant),
                        None)

                    if dedicated_target is not None:
                        direction = pygame.Vector2(
                            dedicated_target.x - self.player.x, dedicated_target.y - self.player.y)

                        if direction.length_squared() > 0:
                            directions.append(direction.normalize())

                front_target = next(
                    (e for e in ordered_enemies
                     if self._get_quadrant(e.x - self.player.x, e.y - self.player.y) not in claimed_quadrants),
                    None)

                if front_target is not None:
                    direction = pygame.Vector2(
                        front_target.x - self.player.x, front_target.y - self.player.y)

                    if direction.length_squared() > 0:
                        directions.append(direction.normalize())

                if directions:
                    shots = [{"direction": d, "offset": pygame.Vector2(
                        0, 0)} for d in directions]
                    self._create_projectiles(shots)

                    burst_count = int(
                        self.player.get_passive_value("tiro_rajada"))

                    if burst_count > 1:
                        self.player.queue_burst(shots, burst_count - 1)
                    else:
                        self.player.confirm_shot()

            else:
                # --- Diagonal, Paralelo, ou nenhuma variante: comportamento existente ---
                target = self.find_closest_enemy(enemies)

                if target is not None:

                    direction = pygame.Vector2(
                        target.x - self.player.x, target.y - self.player.y)

                    if direction.length_squared() > 0:
                        direction = direction.normalize()

                        shots = self.player.get_shot_vectors(direction)
                        self._create_projectiles(shots)

                        burst_count = int(
                            self.player.get_passive_value("tiro_rajada"))

                        if burst_count > 1:
                            self.player.queue_burst(shots, burst_count - 1)
                        else:
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

        # --- sabre giratorio: sincroniza quantidade, orbita e aplica dano por contato ---
        self.sync_sabers()

        if self.sabers:
            rotation_speed = self.player.get_passive_value("sabre_velocidade")
            saber_damage = self.player.get_passive_value("sabre_dano")

            for saber in self.sabers:
                saber.update(dt, self.player, rotation_speed)

                for enemy in enemies:
                    if not enemy.is_dead and saber.can_hit(enemy) and saber.rect.colliderect(enemy.rect):
                        enemy.take_damage(saber_damage)
                        saber.register_hit(enemy)

                        self.spawn_damage_text(enemy.x, enemy.y, saber_damage)

                        if enemy.is_dead:
                            self.player.register_kill(
                                enemy.enemy_type, enemy.drop_value)
                            self.room.register_kill(
                                enemy.enemy_type, enemy.drop_value)

                            from src.entities.gem import Gem
                            self.gems.append(
                                Gem(enemy.x, enemy.y, enemy.drop_value))

        # --- sifao de energia: raio extrator instantaneo, mira o 2o inimigo mais proximo ---
        if self.siphon_beam is not None:
            start, end, time_left = self.siphon_beam
            time_left -= dt
            self.siphon_beam = (
                start, end, time_left) if time_left > 0 else None

        siphon_damage = self.player.get_passive_value("siphon_dano")

        if self.player.ready_to_siphon() and siphon_damage > 0:
            ordered_enemies = self.get_enemies_by_distance(enemies)

            if len(ordered_enemies) >= 2:
                target = ordered_enemies[1]

                target.take_damage(siphon_damage)
                self.player.confirm_siphon()

                conversion = self.player.get_passive_value("siphon_conversao")

                if conversion > 0:
                    # garante minimo de 1 HP sempre que a conversao estiver ativa -
                    # sem isso, valores baixos de dano x conversao truncariam para 0
                    healed = max(1, round(siphon_damage * conversion))

                    self.player.hp = min(
                        self.player.max_hp, self.player.hp + healed)
                    self.spawn_heal_text(self.player.x, self.player.y, healed)

                self.siphon_beam = (
                    self.player.rect.center, target.rect.center, settings.SIPHON_BEAM_DURATION)

                self.spawn_damage_text(target.x, target.y, siphon_damage)

                if target.is_dead:
                    self.player.register_kill(
                        target.enemy_type, target.drop_value)
                    self.room.register_kill(
                        target.enemy_type, target.drop_value)

                    from src.entities.gem import Gem
                    self.gems.append(
                        Gem(target.x, target.y, target.drop_value))

        # --- campo de forca: pulso de dano em area, atingindo todos os inimigos dentro do raio ---
        field_radius = self.player.get_passive_value("campo_area")

        if field_radius > 0 and self.player.force_field_timer <= 0:
            field_damage = self.player.get_passive_value("campo_dano")

            self.player.force_field_timer = settings.FORCE_FIELD_TICK_INTERVAL

            for enemy in enemies:
                if enemy.is_dead:
                    continue

                distance = pygame.Vector2(
                    enemy.x - self.player.x, enemy.y - self.player.y).length()

                if distance <= field_radius:
                    enemy.take_damage(field_damage)
                    self.spawn_damage_text(enemy.x, enemy.y, field_damage)

                    if enemy.is_dead:
                        self.player.register_kill(
                            enemy.enemy_type, enemy.drop_value)
                        self.room.register_kill(
                            enemy.enemy_type, enemy.drop_value)

                        from src.entities.gem import Gem
                        self.gems.append(
                            Gem(enemy.x, enemy.y, enemy.drop_value))

        # --- phaser leve: municao limitada, mira o 3o inimigo mais proximo ---
        if self.player.ready_to_fire_phaser():
            ordered_enemies = self.get_enemies_by_distance(enemies)

            if len(ordered_enemies) >= 3:
                target = ordered_enemies[2]

                direction = pygame.Vector2(
                    target.x - self.player.x, target.y - self.player.y)

                if direction.length_squared() > 0:
                    direction = direction.normalize()
                    phaser_damage = self.player.get_passive_value(
                        "phaser_dano")

                    from src.entities.projectile import Projectile
                    self.projectiles.append(Projectile(
                        self.player.x, self.player.y, direction,
                        max_range=self.player.range_radius,
                        damage=phaser_damage, pierce=1, color=(100, 200, 255)))

                    self.player.confirm_phaser_shot()

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
                    damage_taken, was_blocked = self.player.take_damage(
                        enemy.damage)
                    self.player.apply_knockback(enemy.x, enemy.y)

                    if was_blocked:
                        self.spawn_block_text(self.player.x, self.player.y)
                    else:
                        self.spawn_damage_text(
                            self.player.x, self.player.y, damage_taken)

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

        if self.upgrade_choices is not None:
            self.draw_upgrade_choices(screen)

    def draw_background(self, screen: pygame.Surface) -> None:

        screen.fill((18, 20, 30))

        self.room.draw(screen, self.camera_x, self.camera_y)

    def draw_world(self, screen: pygame.Surface) -> None:

        self.entity_manager.draw(screen, self.camera_x, self.camera_y)

        for projectile in self.projectiles:
            projectile.draw(screen, self.camera_x, self.camera_y)

        for gem in self.gems:
            gem.draw(screen, self.camera_x, self.camera_y)

        for saber in self.sabers:
            saber.draw(screen, self.camera_x, self.camera_y)

        if self.siphon_beam is not None:
            start, end, _time_left = self.siphon_beam
            screen_start = (start[0] - self.camera_x, start[1] - self.camera_y)
            screen_end = (end[0] - self.camera_x, end[1] - self.camera_y)
            pygame.draw.line(screen, (140, 220, 160),
                             screen_start, screen_end, width=3)

        for text in self.floating_texts:
            text.draw(screen, self.camera_x, self.camera_y)

    def draw_ui(self, screen: pygame.Surface) -> None:

        # --- elementos essenciais, sempre visiveis ---
        self.draw_score(screen)
        self.draw_session_info(screen)
        self.draw_hp_bar(screen)
        self.draw_progress_bar(screen)
        self.draw_room_and_lives(screen)

        # --- painel de debug, compacto e translucido ---
        self.draw_debug_panel(screen)

    def draw_upgrade_choices(self, screen: pygame.Surface) -> None:

        overlay = pygame.Surface(
            (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 200))
        screen.blit(overlay, (0, 0))

        title_font = pygame.font.Font(None, 36)
        title = title_font.render("Escolha um upgrade", True, (255, 255, 255))
        title_rect = title.get_rect(
            center=(settings.WINDOW_WIDTH / 2, settings.WINDOW_HEIGHT / 2 - 80))
        screen.blit(title, title_rect)

        option_font = pygame.font.Font(None, 28)

        for i, key in enumerate(self.upgrade_choices):
            label = settings.UPGRADE_LABELS.get(key, key)
            text = option_font.render(
                f"[{i + 1}] {label}", True, (220, 220, 220))
            text_rect = text.get_rect(
                center=(settings.WINDOW_WIDTH / 2, settings.WINDOW_HEIGHT / 2 - 20 + i * 40))
            screen.blit(text, text_rect)

    def draw_score(self, screen: pygame.Surface) -> None:

        room_points = sum(self.room.points_by_type.values())
        total_points = sum(self.player.points_by_type.values())

        font_room = pygame.font.Font(None, 24)
        text_room = font_room.render(
            f"Sala: {room_points:.0f} pts", True, (255, 255, 255))
        text_room_rect = text_room.get_rect()
        text_room_rect.topleft = (20, 2)
        screen.blit(text_room, text_room_rect)

        font_total = pygame.font.Font(None, 18)
        text_total = font_total.render(
            f"Total: {total_points:.0f} pts", True, (170, 170, 170))
        text_total_rect = text_total.get_rect()
        text_total_rect.topleft = (20, 20)
        screen.blit(text_total, text_total_rect)

    def draw_session_info(self, screen: pygame.Surface) -> None:

        total_seconds = int(self.session_time)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        rooms_cleared = sum(room.times_cleared for room in self.rooms.values())

        font = pygame.font.Font(None, 18)
        text = font.render(
            f"{hours:02d}:{minutes:02d}:{seconds:02d}  |  Salas limpas: {rooms_cleared}",
            True, (170, 170, 170))
        text_rect = text.get_rect()
        text_rect.topright = (settings.WINDOW_WIDTH - 20, 2)
        screen.blit(text, text_rect)

    def draw_hp_bar(self, screen: pygame.Surface) -> None:

        bar_x, bar_y = 20, 46
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

        bar_x, bar_y = 20, 72
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

        base_text = f"Room {self.room.room_id}  |  Vidas: {self.player.lives}/{self.player.max_lives}"

        # phaser leve: mostra municao atual ou aviso de recarga, so se a arma ja foi adquirida
        if self.player.passive_levels["phaser_capacidade"] > 0:
            if self.player.phaser_reload_timer > 0:
                base_text += "  |  Phaser: recarregando..."
            else:
                capacity = int(
                    self.player.get_passive_value("phaser_capacidade"))
                base_text += f"  |  Phaser: {self.player.phaser_ammo}/{capacity}"

        font = pygame.font.Font(None, 26)
        text = font.render(base_text, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.topleft = (20, 88)
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
        panel_x, panel_y = 20, 118

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

        # --- sempre visivel: essencial para decisao imediata durante o jogo ---
        lines = []

        lines.append(
            f"Visitas: {self.room.times_cleared}  |  "
            f"Reentradas: {self.room.reentries}/{self.room.max_reentries}")

        lines.append(self._build_survival_line())
        lines.append(self._build_enemy_counter_line())
        lines.append(self._build_progress_line())
        lines.append(
            f"Slots: {len(self.player.get_equipped_categories())}/{self.player.get_max_powerup_slots()}")
        lines.append(self._build_powerup_summary_line())
        lines.append("")
        lines.append("[TAB] historico detalhado")

        if not self.debug_expanded:
            return lines

        # --- expandido (TAB): historico acumulado, so quando solicitado ---
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

    def _build_powerup_summary_line(self) -> str:

        # resumo compacto: so categorias equipadas (nivel > 0 em algum eixo), sigla + maior nivel
        equipped = sorted(self.player.get_equipped_categories())

        if not equipped:
            return "Power-ups: nenhum"

        parts = []

        for category in equipped:
            label = settings.CATEGORY_LABELS.get(category, category)
            max_level = self.player.get_category_max_level(category)
            parts.append(f"{label}-{max_level}")

        return "Power-ups: " + " ".join(parts)

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
