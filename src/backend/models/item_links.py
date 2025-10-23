from dataclasses import dataclass


@dataclass
class ItemLinks:
    related: str
    self: str

    def __init__(self, raw_data: dict):
        self.related = raw_data.get("related") or ""
        self.self = raw_data.get("self") or ""

