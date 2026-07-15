import pygame

import settings

from scenes.game_scene import GameScene


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))

        pygame.display.set_caption(settings.WINDOW_TITLE)

        self.clock = pygame.time.Clock()

        self.scene = GameScene()

    def run(self):
        running = True

        while running:
            dt = self.clock.tick(settings.FPS) / 1000

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                self.scene.handle_event(event)

            self.scene.update(dt)

            self.scene.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
