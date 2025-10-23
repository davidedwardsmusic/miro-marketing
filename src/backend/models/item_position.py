from dataclasses import dataclass


@dataclass
class ItemPosition:
    origin: str
    relative_to: str
    x: float
    y: float

    def __init__(self, raw_data: dict):
        self.origin = raw_data.get("origin") or ""
        self.relative_to = raw_data.get("relativeTo") or ""
        self.x = raw_data.get("x") or 0.0
        self.y = raw_data.get("y") or 0.0

