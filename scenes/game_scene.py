import pygame

from scenes.scene import Scene

from systems.entity_manager import EntityManager

from entities.player import Player


class GameScene(Scene):
    def __init__(self):
        self.entity_manager = EntityManager()

        self.player = Player(200, 150)

        self.entity_manager.add(self.player)

    def handle_event(self, event):
        pass

    def update(self, dt: float):
        self.entity_manager.update(dt)

    def draw(self, screen):
        self.draw_background(screen)
        self.draw_world(screen)
        self.draw_ui(screen)

    def draw_background(self, screen):

        screen.fill((18, 20, 30))

        room = pygame.Rect(80, 60, 640, 480,)

        wall = 20

        # Piso
        pygame.draw.rect(screen, (55, 60, 70), room,)

        # Parede Superior
        pygame.draw.rect(screen, (95, 100, 115),
                         (room.left, room.top, room.width, wall),)

        # Parede Inferior
        pygame.draw.rect(screen, (95, 100, 115), (room.left,
                         room.bottom - wall, room.width, wall),)

        # Parede Esquerda
        pygame.draw.rect(screen, (95, 100, 115),
                         (room.left, room.top, wall, room.height),)

        # Parede Direita
        pygame.draw.rect(screen, (95, 100, 115),
                         (room.right - wall, room.top, wall, room.height),)

        # Contorno
        pygame.draw.rect(screen, (120, 130, 145), room, width=3,)

    def draw_world(self, screen):
        self.entity_manager.draw(screen)

    def draw_ui(self, screen):
        pass
