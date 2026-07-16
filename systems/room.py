import pygame


class Room:

    def __init__(self, x, y, width, height, wall=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.wall = wall
        self.spawn = (self.rect.centerx - 16, self.rect.centery - 16,)
        self.doors = []

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

        for door in self.doors:
            door.draw(screen)

    def get_bounds(self):

        return (self.rect.left + self.wall,
                self.rect.top + self.wall,
                self.rect.right - self.wall,
                self.rect.bottom - self.wall,
                )

    def get_spawn(self):
        return self.spawn

    def add_door(self, door):

        self.doors.append(door)

    def get_doors(self):

        return self.doors

    def get_colliding_door(self, player):

        for door in self.doors:

            if door.collides(player):
                return door
        return None
