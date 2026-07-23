import pygame
from src.entities.entity import Entity


class EntityManager:
    def __init__(self) -> None:
        self.entities: list[Entity] = []

    def add(self, entity: Entity) -> None:
        self.entities.append(entity)

    def update(self, dt: float) -> None:
        for entity in self.entities:
            entity.update(dt)

    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        for entity in self.entities:
            entity.draw(screen, camera_x, camera_y)
