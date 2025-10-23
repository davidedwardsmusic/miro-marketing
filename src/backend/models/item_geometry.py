from dataclasses import dataclass
import random

from prompt_toolkit.data_structures import Point


@dataclass
class ItemGeometry:
    width: float
    height: float

    def __init__(self, raw_data: dict):
        self.width = raw_data.get("width") or 0.0
        self.height = raw_data.get("height") or 0.0

    def get_random_position(self) -> Point:
        x = random.randint(0, int(self.width - 100))
        y = random.randint(0, int(self.height - 100))
        return Point(x, y)

