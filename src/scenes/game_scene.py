import pygame

from src.scenes.scene import Scene

from src.systems.entity_manager import EntityManager

from src.entities.player import Player

from src.systems.room import Room

from src.systems.door import Door, TOP, BOTTOM


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

        }
        self.room_data = {
            1: {
                "doors": [1, 2],
            },
            2: {
                "doors": [3],
            },
            3: {
                "doors": [4],
            }
        }
        self.current_room_id: int = 1
        self.room: Room = self.create_room(self.current_room_id)

        spawn_x, spawn_y = self.room.get_spawn()
        self.player: Player = Player(spawn_x, spawn_y,)
        self.player.room = self.room

        self.entity_manager.add(self.player)

        self.last_state: str | None = None

    def create_room(self, room_id: int) -> Room:

        if room_id in self.rooms:
            return self.rooms[room_id]

        room = Room(80, 60, 640, 480)

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

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:

        self.entity_manager.update(dt)

        if self.player.consume_room_change():

            target_door_id = self.player.current_door.target_door

            self.current_room_id = self.door_data[target_door_id]["room"]

            self.room = self.create_room(self.current_room_id)

            self.player.room = self.room

            target_door = self.room.get_door_by_id(target_door_id)

            spawn_x, spawn_y = target_door.get_spawn_position()

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
                    self.player.target_position = door.get_entry_target()

                    self.player.state = "entering_door"

                    target_room = self.door_data[door.target_door]["room"]
                    print(f"Door -> {door.side} -> Room {target_room}")

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
