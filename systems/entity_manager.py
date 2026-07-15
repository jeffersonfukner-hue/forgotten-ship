from entities.entity import Entity


class EntityManager:
    def __init__(self):
        self.entities: list[Entity] = []

    def add(self, entity: Entity):
        self.entities.append(entity)

    def update(self, dt: float):
        for entity in self.entities:
            entity.update(dt)

    def draw(self, screen):
        for entity in self.entities:
            entity.draw(screen)
