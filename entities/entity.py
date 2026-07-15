class Entity:
    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = x
        self.y = y

        self.width = width
        self.height = height

    def update(self, dt: float):
        pass

    def draw(self, screen):
        pass
