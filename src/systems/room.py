import pygame

from src.systems.door import Door

from src.entities.player import Player


class Room:

    def __init__(self, x: int, y: int, width: int, height: int, room_id: int, wall: int = 20) -> None:
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.wall: int = wall
        self.room_id: int = room_id
        self.doors: list[Door] = []

    def draw(self, screen: pygame.Surface,) -> None:

        # Piso
        pygame.draw.rect(screen, (55, 60, 70), self.rect,)

        # Parede Superior
        pygame.draw.rect(screen, (95, 100, 115), (self.rect.left,
                         self.rect.top, self.rect.width, self.wall),)

        # Parede Inferior
        pygame.draw.rect(screen, (95, 100, 115), (self.rect.left,
                         self.rect.bottom - self.wall, self.rect.width, self.wall),)

        # Parede Esquerda
        pygame.draw.rect(screen, (95, 100, 115), (self.rect.left,
                         self.rect.top, self.wall, self.rect.height),)

        # Parde Direita
        pygame.draw.rect(screen, (95, 100, 115), (self.rect.right -
                         self.wall, self.rect.top, self.wall, self.rect.height),)

        # Contorno
        pygame.draw.rect(screen, (145, 150, 165), self.rect, width=2,)

        # Numerar as salas

        font = pygame.font.Font(None, 32)

        text = font.render(f"Room {self.room_id}", True, (255, 255, 255))

        text_rect = text.get_rect()
        text_rect.topleft = (self.rect.left + 12, self.rect.top + 12)

        screen.blit(text, text_rect)

        for door in self.doors:
            door.draw(screen)

    def get_bounds(self) -> tuple[int, int, int, int]:

        return (self.rect.left + self.wall,
                self.rect.top + self.wall,
                self.rect.right - self.wall,
                self.rect.bottom - self.wall,
                )

    def add_door(self, door: Door) -> None:

        self.doors.append(door)

    def get_doors(self) -> list[Door]:

        return self.doors

    def get_colliding_door(self, player: Player) -> Door | None:

        for door in self.doors:

            if door.collides(player):
                return door
        return None

    def get_door_by_id(self, door_id: int) -> Door | None:

        for door in self.doors:
            if door.id == door_id:
                return door

        return None
