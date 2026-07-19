import pygame

from scenes.scene import Scene

from systems.entity_manager import EntityManager

from entities.player import Player

from systems.room import Room

from systems.door import Door, TOP, BOTTOM


class GameScene(Scene):
    def __init__(self) -> None:

        self.entity_manager: EntityManager = EntityManager()

        self.current_room_id: int = 1
        self.room: Room = self.create_room(self.current_room_id)

        spawn_x, spawn_y = self.room.get_spawn()
        self.player: Player = Player(spawn_x, spawn_y,)
        self.player.room = self.room

        self.entity_manager.add(self.player)

        self.last_state: str | None = None

    def create_room(self, room_id: int) -> Room:

        room = Room(80, 60, 640, 480)

        if room_id == 1:
            room.add_door(Door(x=340, y=60, width=40,
                          height=20, side=TOP, target_room=2))

        elif room_id == 2:
            room.add_door(Door(x=340, y=520, width=40,
                          height=20, side=BOTTOM, target_room=1))

        return room

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:

        self.entity_manager.update(dt)

        if self.player.consume_room_change():

            self.current_room_id = self.player.current_door.target_room

            self.room = self.create_room(self.current_room_id)

            self.player.room = self.room

            spawn_x, spawn_y = self.room.get_spawn()

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

                    print(f"Door -> {door.side} -> Room {door.target_room}")

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
