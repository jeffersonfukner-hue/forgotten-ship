import pygame

from src.scenes.scene import Scene

from src.systems.entity_manager import EntityManager

from src.entities.player import Player

from src.systems.room import Room

from src.systems.door import Door, TOP, BOTTOM, LEFT, RIGHT

from src import settings


class GameScene(Scene):
    def __init__(self) -> None:

        self.entity_manager: EntityManager = EntityManager()

        from src.entities.projectile import Projectile
        self.projectiles: list[Projectile] = []

        self.rooms: dict[int, Room] = {}

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

        self.current_room_id: int = 1
        self.room: Room = self.create_room(self.current_room_id)

        spawn_x, spawn_y = self.room_data[self.current_room_id]["spawn"]
        self.player: Player = Player(spawn_x, spawn_y,)
        self.player.room = self.room
        self.entity_manager.add(self.player)

        self.last_state: str | None = None
        self.camera_x: float = 0.0
        self.camera_y: float = 0.0

    def find_closest_enemy(self, enemies: list):

        closest = None
        closest_distance = None

        for enemy in enemies:
            distance = pygame.Vector2(
                enemy.x - self.player.x, enemy.y - self.player.y).length()

            if closest_distance is None or distance < closest_distance:
                closest = enemy
                closest_distance = distance

        return closest

   # dimensoes de cada sala: Area de Carga (grande), Corredor (longo e estreito), Engenharia
    ROOM_SIZES = {
        1: (1280, 960),
        2: (300, 1400),
        3: (900, 700),
    }

    def create_room(self, room_id: int) -> Room:

        if room_id in self.rooms:
            return self.rooms[room_id]

        width, height = self.ROOM_SIZES[room_id]
        room = Room(80, 60, width, height, room_id=room_id)

        self.configure_room(room, room_id)

        self.rooms[room_id] = room

        return room

    def configure_room(self, room: Room, room_id: int) -> None:

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

        if room_id == 1:

            from src.entities.enemy import Enemy
            import random

            left, top, right, bottom = room.get_bounds()

            for _ in range(3):
                # escolhe uma borda aleatoria (0=topo, 1=baixo, 2=esquerda, 3=direita)
                edge = random.randint(0, 3)

                if edge == 0:
                    x, y = random.randint(left, right), top
                elif edge == 1:
                    x, y = random.randint(left, right), bottom
                elif edge == 2:
                    x, y = left, random.randint(top, bottom)
                else:
                    x, y = right, random.randint(top, bottom)

                room.add_enemy(Enemy(x, y))
        # tranca todas as portas da sala se ela tiver inimigos - destranca quando a sala for limpa
        if room.get_enemies():
            for door in room.get_doors():
                door.lock()

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:

        self.entity_manager.update(dt)
        self.update_camera()

        # limpa inimigos derrotados antes de processar a sala
        self.room.remove_dead_enemies()

        if not self.room.get_enemies():
            # sala limpa: destranca todas as portas
            for door in self.room.get_doors():
                door.unlock()

        enemies = self.room.get_enemies()

        if self.player.ready_to_shoot() and enemies:
            target = self.find_closest_enemy(enemies)

            if target is not None:

                direction = pygame.Vector2(
                    target.x - self.player.x, target.y - self.player.y)

                if direction.length_squared() > 0:
                    direction = direction.normalize()

                    from src.entities.projectile import Projectile
                    self.projectiles.append(Projectile(
                        self.player.x, self.player.y, direction))

                    self.player.confirm_shot()

        for projectile in self.projectiles:
            projectile.update(dt)

            for enemy in enemies:
                if not enemy.is_dead and projectile.rect.colliderect(enemy.rect):
                    enemy.take_damage(projectile.damage)
                    projectile.is_dead = True
                    break  # projetil atinge apenas 1 inimigo por enquanto

        left, top, right, bottom = self.room.get_bounds()

        for projectile in self.projectiles:
            if (projectile.x < left or projectile.x > right
                    or projectile.y < top or projectile.y > bottom):
                projectile.is_dead = True  # saiu da area jogavel, marca para remocao

        self.projectiles = [p for p in self.projectiles if not p.is_dead]

        if not self.player.is_dead:  # inimigos param de agir assim que o jogador morre

            for enemy in enemies:
                enemy.update(dt, self.player.x, self.player.y, enemies)

            for enemy in enemies:
                if self.player.rect.colliderect(enemy.rect):
                    self.player.take_damage(10)
                    self.player.apply_knockback(enemy.x, enemy.y)
                    print(f"HP -> {self.player.hp}")

                    if self.player.is_dead:
                        print("GAME OVER")
                    break
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

                    alignment_point = door.get_alignment_point(
                        self.player.x, self.player.y, self.player.width, self.player.height)
                    entry_point = door.get_entry_target(
                        self.player.width, self.player.height)

                    self.player.start_door_sequence(
                        [alignment_point, entry_point], door.get_thickness())

                    self.player.state = "entering_door"

                target_room_id = self.door_data[door.target_door]["room"]
                print(f"Door -> {door.side} -> Room {target_room_id}")

        else:

            if self.player.state == "walking":
                self.player.current_door = None

    def update_camera(self) -> None:

        room_rect = self.room.rect

        if room_rect.width <= settings.WINDOW_WIDTH:
            # sala menor que a tela nesse eixo: centraliza a sala, nao segue o player
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

    def draw_ui(self, screen: pygame.Surface) -> None:
        pass
