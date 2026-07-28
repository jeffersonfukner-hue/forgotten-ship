import pygame

from src import settings

from src.scenes.game_scene import GameScene


class Game:
    """Ponto de entrada do jogo: inicializa a janela e o pygame, mantem
    a cena atual (hoje sempre GameScene, criada uma unica vez por
    sessao) e roda o loop principal ate o jogador fechar a janela."""

    def __init__(self) -> None:
        pygame.init()

        # --- janela e relogio ---
        self.screen: pygame.Surface = pygame.display.set_mode(
            (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))

        pygame.display.set_caption(settings.WINDOW_TITLE)

        self.clock: pygame.time.Clock = pygame.time.Clock()

        # --- cena atual: unica instancia por sessao inteira de jogo ---
        self.scene: GameScene = GameScene()

    # ==================================================================
    # LOOP PRINCIPAL
    # ==================================================================

    def run(self) -> None:

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
