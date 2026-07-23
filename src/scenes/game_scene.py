import pygame

from src.scenes.scene import Scene

from src.systems.entity_manager import EntityManager

from src.entities.player import Player

from src.systems.room import Room

from src.systems.door import Door, TOP, BOTTOM, LEFT, RIGHT


class GameScene(Scene):
    def __init__(self) -> None:

        self.entity_manager: EntityManager = EntityManager()

        self.rooms: dict[int, Room] = {}
        self.door_data = {
            1: {
                "room": 1,
                "x": 340,
                "y": 60,
                "width": 40,
                "height": 20,
                "side": TOP,
                "target": 3,
            },
            2: {
                "room": 1,
                "x": 340,
                "y": 520,
                "width": 40,
                "height": 20,
                "side": BOTTOM,
                "target": 4,
            },
            3: {
                "room": 2,
                "x": 340,
                "y": 520,
                "width": 40,
                "height": 20,
                "side": BOTTOM,
                "target": 1,
            },
            4: {
                "room": 3,
                "x": 340,
                "y": 60,
                "width": 40,
                "height": 20,
                "side": TOP,
                "target": 2,
            },
            5: {
                "room": 3,
                "x": 80,
                "y": 260,
                "width": 20,
                "height": 40,
                "side": LEFT,
                "target": 6,
            },
            6: {
                "room": 4,
                "x": 700,
                "y": 260,
                "width": 20,
                "height": 40,
                "side": RIGHT,
                "target": 5,
            },
            7: {
                "room": 4,
                "x": 340,
                "y": 520,
                "width": 40,
                "height": 20,
                "side": BOTTOM,
                "target": 8,
            },
            8: {
                "room": 5,
                "x": 340,
                "y": 60,
                "width": 40,
                "height": 20,
                "side": TOP,
                "target": 7,
            },
        }
        self.room_data = {
            1: {
                "doors": [1, 2],
                "spawn": (384, 284),
            },
            2: {
                "doors": [3],
            },
            3: {
                "doors": [4, 5],
            },
            4: {
                "doors": [6, 7],
            },
            5: {
                "doors": [8],
            },
        }

        self.current_room_id: int = 1
        self.room: Room = self.create_room(self.current_room_id)

        spawn_x, spawn_y = self.room_data[self.current_room_id]["spawn"]
        self.player: Player = Player(spawn_x, spawn_y,)
        self.player.room = self.room
        self.entity_manager.add(self.player)

        self.last_state: str | None = None

    def create_room(self, room_id: int) -> Room:

        if room_id in self.rooms:
            return self.rooms[room_id]

        room = Room(80, 60, 640, 480, room_id=room_id)

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

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:

        self.entity_manager.update(dt)

        enemies = self.room.get_enemies()

        for enemy in self.room.get_enemies():
            enemy.update(dt, self.player.x, self.player.y, enemies)

        if not self.player.is_dead:
            for enemy in self.room.get_enemies():
                if self.player.rect.colliderect(enemy.rect):
                    self.player.take_damage(10)
                    self.player.apply_knockback(enemy.x, enemy.y)
                    print(f"HP -> {self.player.hp}")

                    if self.player.is_dead:
                        print("GAME OVER")
                    break  # evita levar dano de 2 inimigos no mesmo frame

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

    def draw(self, screen: pygame.Surface) -> None:
        self.draw_background(screen)
        self.draw_world(screen)
        self.draw_ui(screen)

    def draw_background(self, screen: pygame.Surface) -> None:

        screen.fill((18, 20, 30))

        self.room.draw(screen)

    def draw_world(self, screen: pygame.Surface) -> None:
        self.entity_manager.draw(screen)

    def draw_ui(self, screen: pygame.Surface) -> None:
        pass
