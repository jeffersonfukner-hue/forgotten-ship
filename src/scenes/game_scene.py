import pygame

from src.scenes.scene import Scene

from src.systems.entity_manager import EntityManager

from src.entities.player import Player

from src.systems.room import Room

from src.systems.door import Door, TOP, BOTTOM, LEFT, RIGHT

from src import settings


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

    # ==================================================================
    # CRIACAO E CONFIGURACAO DE SALAS
    # ==================================================================

    def spawn_horde(self, room: Room) -> None:
        """Gera uma nova horda de inimigos na sala, espalhados nas bordas,
        respeitando distancia minima das portas. Reinicia o cronometro de onda."""

        from src.entities.enemy import Enemy
        import random
        import time

        room.horde_start_time = time.time()
        room.horde_clear_time = None  # None enquanto a horda estiver ativa

        # TESTE: valor reduzido para agilizar testes de reentrada/regeneracao.
        # Formula real (Sprint 012): 12 + (room.times_cleared * 6)
        enemy_count = (settings.HORDE_BASE_ENEMIES
                       + room.times_cleared * settings.HORDE_ENEMIES_PER_VISIT)
        
        room.horde_total_enemies = enemy_count

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

            room.add_enemy(Enemy(x, y))

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

        # --- limpeza e destravamento de sala ---
        self.room.remove_dead_enemies()

        if not self.room.get_enemies() and not self.room.cleared:
            # sala limpa pela primeira vez neste ciclo: destranca portas e marca como limpa
            for door in self.room.get_doors():
                door.unlock()

            self.room.cleared = True
            self.room.times_cleared += 1

            import time
            self.room.horde_clear_time = time.time() - self.room.horde_start_time

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
                        max_range=self.player.range_radius))

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
                    self.player.take_damage(10)
                    self.player.apply_knockback(enemy.x, enemy.y)

                    self.spawn_damage_text(
                        self.player.x, self.player.y, 10)

                    print(f"HP -> {self.player.hp}")

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
                        print("Sem reentradas disponiveis - aguarde regenerar")
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

        # --- elementos fixos de HUD, na ordem de leitura ---
        self.draw_hp_bar(screen)
        self.draw_room_info(screen)
        self.draw_lives_counter(screen)
        self.draw_wave_timer(screen)
        self.draw_enemy_counter(screen)
        self.draw_all_rooms_debug(screen)

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

    def draw_room_info(self, screen: pygame.Surface) -> None:

        self.room.regen_reentries()  # forca o calculo de regeneracao a cada frame, para a HUD refletir o tempo real

        font = pygame.font.Font(None, 28)
        text = font.render(
            f"Room {self.room.room_id}  (visitas: {self.room.times_cleared}, "
            f"reentradas: {self.room.reentries}/{self.room.max_reentries})",
            True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.topleft = (20, 52)
        screen.blit(text, text_rect)

    def draw_all_rooms_debug(self, screen: pygame.Surface) -> None:

        font = pygame.font.Font(None, 24)

        y = 180  # abaixo do contador de inimigos

        for room_id in sorted(self.rooms.keys()):
            room = self.rooms[room_id]
            room.regen_reentries()  # forca atualizacao antes de exibir

            timer_text = f"{room.time_until_next_regen():.0f}s" if room.reentries < room.max_reentries else "cheio"

            text = font.render(
                f"Room {room_id}: {room.reentries}/{room.max_reentries} ({timer_text})",
                True, (200, 200, 200))
            text_rect = text.get_rect()
            text_rect.topleft = (20, y)
            screen.blit(text, text_rect)

            y += 24

    def draw_lives_counter(self, screen: pygame.Surface) -> None:

        font = pygame.font.Font(None, 28)
        text = font.render(
            f"Vidas: {self.player.lives}/{self.player.max_lives}", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.topleft = (20, 84)
        screen.blit(text, text_rect)

    def draw_wave_timer(self, screen: pygame.Surface) -> None:

        import time

        if self.room.horde_clear_time is not None:
            elapsed = self.room.horde_clear_time
            label = "Onda concluida em"
        elif self.room.get_enemies():
            elapsed = time.time() - self.room.horde_start_time
            label = "Tempo de onda"
        else:
            return  # sala sem horda ativa (ex: sala ja limpa e ainda nao reentrou)

        font = pygame.font.Font(None, 28)
        text = font.render(f"{label}: {elapsed:.1f}s", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.topleft = (20, 116)
        screen.blit(text, text_rect)

    def draw_enemy_counter(self, screen: pygame.Surface) -> None:

        total = self.room.horde_total_enemies

        if total == 0:
            return  # sala sem horda gerada ainda (ex: sala vazia por design)

        remaining = len(self.room.get_enemies())

        font = pygame.font.Font(None, 28)
        text = font.render(
            f"Inimigos: {remaining}/{total}", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.topleft = (20, 148)
        screen.blit(text, text_rect)