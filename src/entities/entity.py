import pygame


class Entity:
    """Classe base para qualquer objeto do jogo com posicao e tamanho
    (player, inimigo, projetil, obstaculo, etc.). Subclasses sobrescrevem
    update() e draw() com seu comportamento especifico."""

    def __init__(self, x: float, y: float, width: int, height: int) -> None:

        # --- posicao e dimensoes ---
        self.x: float = x
        self.y: float = y
        self.width: int = width
        self.height: int = height

        self.rect: pygame.Rect = pygame.Rect(
            self.x, self.y, self.width, self.height)

    # ==================================================================
    # ATUALIZACAO POR FRAME
    # ==================================================================

    def update(self, dt: float) -> None:
        pass

    # ==================================================================
    # DESENHO
    # ==================================================================

    def draw(self, screen: pygame.Surface) -> None:
        pass
