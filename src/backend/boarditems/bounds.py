from dataclasses import dataclass


@dataclass
class Bounds:
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    id: str = ''

    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def fix_x(self):
        return self.x + (self.width / 2)

    def fix_y(self):
        return self.y + (self.height / 2)

    def position(self) -> dict:
        return {"x": self.fix_x(), "y": self.fix_y()}
