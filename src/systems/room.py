import pygame

from src.systems.door import Door

from src.entities.player import Player


class Room:

    def __init__(self, x: int, y: int, width: int, height: int, room_id: int, wall: int = 20) -> None:
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.wall: int = wall
        self.room_id: int = room_id
        self.doors: list[Door] = []
        # tipo Enemy, import evitado aqui p/ nao criar dependencia circular
        self.enemies: list = []

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

    def add_enemy(self, enemy) -> None:

        self.enemies.append(enemy)

    def get_enemies(self) -> list:

        return self.enemies

    def remove_dead_enemies(self) -> None:

        self.enemies = [e for e in self.enemies if not e.is_dead]

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

    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:

        # todas as coordenadas da sala sao deslocadas pela camera antes de desenhar
        rl, rt = self.rect.left - camera_x, self.rect.top - camera_y

        # Piso
        pygame.draw.rect(
            screen, (55, 60, 70), (rl, rt, self.rect.width, self.rect.height),)

        # Parede Superior
        pygame.draw.rect(screen, (95, 100, 115),
                         (rl, rt, self.rect.width, self.wall),)

        # Parede Inferior
        pygame.draw.rect(screen, (95, 100, 115), (rl,
                                                  rt + self.rect.height - self.wall, self.rect.width, self.wall),)

        # Parede Esquerda
        pygame.draw.rect(screen, (95, 100, 115),
                         (rl, rt, self.wall, self.rect.height),)

        # Parde Direita
        pygame.draw.rect(screen, (95, 100, 115), (rl + self.rect.width -
                                                  self.wall, rt, self.wall, self.rect.height),)

        # Contorno
        pygame.draw.rect(screen, (145, 150, 165),
                         (rl, rt, self.rect.width, self.rect.height), width=2,)

        font = pygame.font.Font(None, 32)

        text = font.render(f"Room {self.room_id}", True, (255, 255, 255))

        text_rect = text.get_rect()
        text_rect.topleft = (rl + 12, rt + 12)

        screen.blit(text, text_rect)

        for door in self.doors:
            door.draw(screen, camera_x, camera_y)

        for enemy in self.enemies:
            enemy.draw(screen, camera_x, camera_y)
