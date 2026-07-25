import pygame

from src.scenes.scene import Scene

from src.systems.entity_manager import EntityManager

from src.entities.player import Player

from src.systems.room import Room

from src.systems.door import Door, TOP, BOTTOM, LEFT, RIGHT

from src import settings

import time

class GameScene(Scene):

    # --- tabelas de configuracao (candidatas a settings.py numa proxima Sprint) ---

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

        self.rooms: dict[int, Room] = {}

        # --- dados de portas: cada porta conhece sua sala, posicao e porta destino ---
        # Nivel 1: Area de Carga - sala inicial, uma porta ao sul leva ao Nivel 2
        # Nivel 2: Corredor conectando a Area de Carga a Engenharia
        self.door_data = {
            1: {
                "room": 1,
                "x": 700,
                "y": 1000,  # borda sul da Area de Carga (bottom - wall)
                "width": 40,
                "height": 20,
                "side": BOTTOM,
                "target": 2,  # leva ao Corredor
            },
            2: {
                "room": 2,
                "x": 210,
                "y": 60,  # borda norte do Corredor
                "width": 40,
                "height": 20,
                "side": TOP,
                "target": 1,  # volta a Area de Carga
            },
            3: {
                "room": 2,
                "x": 210,
                "y": 1440,  # borda sul do Corredor
                "width": 40,
                "height": 20,
                "side": BOTTOM,
                "target": 4,  # leva a Engenharia
            },
            4: {
                "room": 3,
                "x": 510,
                "y": 60,  # borda norte da Engenharia
                "width": 40,
                "height": 20,
                "side": TOP,
                "target": 3,  # volta ao Corredor
            },
        }

        # --- dados de sala: cada sala conhece seu nivel e quais portas possui ---
        self.room_data = {
            1: {
                "level": 1,
                "doors": [1],
                "spawn": (704, 524),  # centro da Area de Carga
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

        # --- sala inicial e jogador ---
        self.current_room_id: int = 1
        self.room: Room = self.create_room(self.current_room_id)

        spawn_x, spawn_y = self.room_data[self.current_room_id]["spawn"]
        self.player: Player = Player(spawn_x, spawn_y,)
        self.player.room = self.room
        self.entity_manager.add(self.player)

        # --- estado auxiliar de log e camera ---
        self.last_state: str | None = None
        self.camera_x: float = 0.0
        self.camera_y: float = 0.0

        # --- progressao: pontos de drop e upgrades ---
        self.drop_points: int = 0
        self.points_to_upgrade: int = settings.POINTS_PER_UPGRADE
        self.shoot_damage: int = settings.PLAYER_SHOOT_DAMAGE  # pode subir com upgrades

    # ==================================================================
    # CRIACAO E CONFIGURACAO DE SALAS
    # ==================================================================

    def spawn_horde(self, room: Room) -> None:
        """Preenche a sala com o piso minimo de inimigos e inicia o
        cronometro de sobrevivencia. Diferente do modelo antigo de ondas
        discretas (Sprint 021-023), a sala mantem uma quantidade minima
        de inimigos vivos o tempo todo, reabastecida continuamente."""

        room.survival_start_time = time.time()
        room.time_expired = False

        enemy_count = settings.HORDE_BASE_ENEMIES
        room.horde_total_enemies = enemy_count

        self._spawn_wave_enemies(room, enemy_count)

    def _spawn_wave_enemies(self, room: Room, enemy_count: int, enemy_type: str = "weak") -> None:
        """Sorteia posicoes nas bordas da sala para uma leva de inimigos,
        respeitando distancia minima das portas. Reutilizado tanto pela
        primeira onda (spawn_horde) quanto pelas ondas seguintes."""

        from src.entities.enemy import Enemy
        import random

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

            room.add_enemy(Enemy(x, y, enemy_type=enemy_type))

    def calculate_wave_time(self, enemy_count: int) -> float:

        import math

        # tempo estimado para o player limpar a onda no ritmo atual de dano/cadencia
        enemy_hp = 20  # HP atual do Enemy (Sprint 013) - fixo por enquanto, sem tipos variados
        shots_per_enemy = math.ceil(enemy_hp / settings.PLAYER_SHOOT_DAMAGE)
        time_per_enemy = shots_per_enemy * settings.PLAYER_SHOOT_INTERVAL

        return enemy_count * time_per_enemy
    
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
        e gera a primeira horda (trancando as portas se houver inimigos)."""

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
        percepcao (player.range_radius), ou None se nenhum estiver ao alcance."""

        closest = None
        closest_distance = None

        for enemy in enemies:
            distance = pygame.Vector2(
                enemy.x - self.player.x, enemy.y - self.player.y).length()

            if distance > self.player.range_radius:
                continue  # fora do alcance de percepcao, ignora

            if closest_distance is None or distance < closest_distance:
                closest = enemy
                closest_distance = distance

        return closest

    # ==================================================================
    # LOOP PRINCIPAL
    # ==================================================================

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:

        # --- entidades e camera ---
        self.entity_manager.update(dt)
        self.update_camera()

        # --- limpeza de inimigos mortos ---
        self.room.remove_dead_enemies()

        # --- piso continuo: reabastece inimigos ate manter o minimo vivo, so enquanto o tempo nao esgotou ---
        current_count = len(self.room.get_enemies())
        missing = self.room.horde_total_enemies - current_count

        if missing > 0 and not self.room.cleared and not self.room.time_expired:
            self._spawn_wave_enemies(self.room, missing)

        # --- condicao de vitoria: sobreviver por tempo determinado (versao simples) ---
        survival_elapsed = time.time() - self.room.survival_start_time

        # ao esgotar o tempo, para de reabastecer - mas so destranca a porta quando nao houver mais inimigos vivos
        if survival_elapsed >= self.room.survival_duration:
            self.room.time_expired = True

        if self.room.time_expired and not self.room.get_enemies() and not self.room.cleared:

            for door in self.room.get_doors():
                door.unlock()

            self.room.cleared = True
            self.room.times_cleared += 1
            self.room.horde_clear_time = survival_elapsed

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

        # --- projeteis: movimento e colisao com inimigos ---
        for projectile in self.projectiles:
            projectile.update(dt)

            for enemy in enemies:
                if not enemy.is_dead and projectile.rect.colliderect(enemy.rect):
                    enemy.take_damage(projectile.damage)
                    projectile.register_hit()  # decrementa pierce; morre quando chega a 0

                    self.spawn_damage_text(
                        enemy.x, enemy.y, projectile.damage)

                    if enemy.is_dead:
                        self.player.add_drop_point(enemy.drop_value)
                        self.player.register_kill(enemy.enemy_type, enemy.drop_value)
                        self.room.register_kill(enemy.enemy_type, enemy.drop_value) 

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

        # --- inimigos: movimento e colisao com o player ---
        if not self.player.is_dead:  # inimigos param de agir assim que o jogador morre

            for enemy in enemies:
                enemy.update(dt, self.player.x, self.player.y, enemies)

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
                        pass  # feedback ja visivel na cor roxa da porta (reentry_blocked)
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

        # fundo da barra (vermelho escuro, representa vida perdida)
        pygame.draw.rect(screen, (80, 30, 30),
                          (bar_x, bar_y, bar_width, bar_height))

        # preenchimento atual (verde, proporcional ao HP restante)
        pygame.draw.rect(screen, (60, 180, 90),
                          (bar_x, bar_y, bar_width * hp_ratio, bar_height))

        # contorno
        pygame.draw.rect(screen, (255, 255, 255),
                          (bar_x, bar_y, bar_width, bar_height), width=2)

        font = pygame.font.Font(None, 24)
        text = font.render(
            f"HP: {self.player.hp}/{self.player.max_hp}", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (bar_x + bar_width / 2, bar_y + bar_height / 2)
        screen.blit(text, text_rect)

    def draw_progress_bar(self, screen: pygame.Surface) -> None:

        bar_x, bar_y = 20, 46  # logo abaixo da barra de HP
        bar_width, bar_height = 200, 10

        ratio = self.player.drop_points / self.player.points_to_upgrade
        ratio = min(1.0, ratio)  # protege contra qualquer excesso momentaneo

        # fundo (roxo escuro, representa progresso faltante)
        pygame.draw.rect(screen, (50, 30, 70),
                          (bar_x, bar_y, bar_width, bar_height))

        # preenchimento (dourado, progresso atual rumo ao proximo upgrade)
        pygame.draw.rect(screen, (200, 170, 60),
                          (bar_x, bar_y, bar_width * ratio, bar_height))

        # contorno
        pygame.draw.rect(screen, (255, 255, 255),
                          (bar_x, bar_y, bar_width, bar_height), width=1)

        font = pygame.font.Font(None, 22)
        text = font.render(f"Level {self.player.level}", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.midleft = (bar_x + bar_width + 10, bar_y + bar_height / 2)
        screen.blit(text, text_rect)

    def draw_room_and_lives(self, screen: pygame.Surface) -> None:

        # linha compacta e essencial: "Room X | Vidas: Y/Z"
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
        panel_x, panel_y = 20, 82

        # fundo translucido, sem borda
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

        self.room.regen_reentries()  # forca o calculo de regeneracao a cada frame, para refletir o tempo real

        lines = []

        lines.append(
            f"Visitas: {self.room.times_cleared}  |  "
            f"Reentradas: {self.room.reentries}/{self.room.max_reentries}")

        lines.append(self._build_survival_line())
        lines.append(self._build_enemy_counter_line())
        lines.append(self._build_progress_line())

        lines.append("")
        lines.append("Estatisticas totais (mortos / pontos):")
        lines.extend(self._build_kill_stat_lines(
            self.player.kills_by_type, self.player.points_by_type))

        lines.append("")  # linha em branco separando o resumo da lista de salas
        lines.append("Salas:")

        for room_id in sorted(self.rooms.keys()):
            room = self.rooms[room_id]
            room.regen_reentries()  # forca atualizacao antes de exibir

            timer_text = (f"{room.time_until_next_regen():.0f}s"
                          if room.reentries < room.max_reentries else "cheio")

            lines.append(
                f"  Room {room_id}: {room.reentries}/{room.max_reentries} ({timer_text})")

            # estatisticas desta sala, aninhadas logo abaixo dela
            for enemy_type in sorted(room.kills_by_type.keys()):
                kills = room.kills_by_type[enemy_type]
                points = room.points_by_type[enemy_type]
                lines.append(
                    f"    {enemy_type}: {kills} mortos, {points:.1f} pts")

        return lines

    def _build_survival_line(self) -> str:

        # piso continuo: mostra tempo sobrevivido, ou o tempo final se a sala ja foi vencida
        if self.room.cleared:
            return f"Sala vencida em: {self.room.horde_clear_time:.1f}s"

        elapsed = time.time() - self.room.survival_start_time
        remaining = max(0.0, self.room.survival_duration - elapsed)

        return f"Sobrevivendo: {elapsed:.1f}s (faltam {remaining:.1f}s)"

    def _build_enemy_counter_line(self) -> str:

        total = self.room.horde_total_enemies

        if total == 0:
            return "Inimigos: --"  # sala sem horda gerada ainda

        current = len(self.room.get_enemies())

        return f"Inimigos vivos: {current} (piso: {total})"

    def _build_progress_line(self) -> str:

        # barra de progresso ja aparece na HUD fixa; aqui so o poder atual, para debug
        return f"Dano do tiro: {self.player.shoot_damage}"

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
    
        if self.room.next_wave_time is not None:
            remaining = max(0.0, self.room.next_wave_time - time.time())
            status = f"Nova onda: {remaining:.1f}s"
        else:
            status = "Ultima onda"

        return f"{status} (onda {self.room.current_wave}/{self.room.total_waves})"