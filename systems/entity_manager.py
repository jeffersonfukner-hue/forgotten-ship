import pygame
from entities.entity import Entity


class EntityManager:
    def __init__(self) -> None:
        self.entities: list[Entity] = []

    def add(self, entity: Entity) -> None:
        self.entities.append(entity)

    def update(self, dt: float) -> None:
        for entity in self.entities:
            entity.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        for entity in self.entities:
            entity.draw(screen)
