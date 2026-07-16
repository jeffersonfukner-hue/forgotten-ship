import pygame

from scenes.scene import Scene

from systems.entity_manager import EntityManager

from entities.player import Player

from systems.room import Room

from systems.door import Door, TOP


class GameScene(Scene):
    def __init__(self):

        self.entity_manager = EntityManager()

        self.room = Room(80, 60, 640, 480)

        spawn_x, spawn_y = self.room.get_spawn()
        self.player = Player(spawn_x, spawn_y,)
        self.player.room = self.room

        self.entity_manager.add(self.player)

        self.room.add_door(Door(x=340, y=60, width=40, height=20, side=TOP,))

    def handle_event(self, event):
        pass

    def update(self, dt: float):

        self.entity_manager.update(dt)

        door = self.room.get_colliding_door(self.player)

        for current_door in self.room.get_doors():
            current_door.close()

        if door:
            door.open()

            if self.player.state == "walking":
                self.player.state = "entering_door"
                print("Entrando na porta...")

    def draw(self, screen):
        self.draw_background(screen)
        self.draw_world(screen)
        self.draw_ui(screen)

    def draw_background(self, screen):

        screen.fill((18, 20, 30))

        self.room.draw(screen)

    def draw_world(self, screen):
        self.entity_manager.draw(screen)

    def draw_ui(self, screen):
        pass
