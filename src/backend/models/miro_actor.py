from dataclasses import dataclass


@dataclass
class MiroActor:
    id: str
    type: str

    def __init__(self, raw_data: dict):
        self.id = raw_data.get("id")
        self.type = raw_data.get("type")

