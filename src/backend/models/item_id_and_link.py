from dataclasses import dataclass

from src.backend.enums.item_id_type import ItemIdType


@dataclass
class ItemIdAndLink:
    id: str
    link: str

    def __init__(self, raw_item: dict, type: ItemIdType):
        match(type):
            case ItemIdType.PARENT:
                self.parse_parent(raw_item)
            case ItemIdType.SELF:
                self.parse_self(raw_item)

    def parse_parent(self, raw_item):
        raw_parent = raw_item.get("parent") or None
        if raw_parent:
            self.id = raw_parent.get("id") or ""
            self.link = raw_parent.get('links').get('self') if raw_parent.get('links') else ''

        else:
            self.id = raw_item.get("parent_id") or ""
            links = raw_item.get("links") or {}
            self.link = links.get("parent") or ""

    def parse_self(self, raw_item):
        self.id = raw_item.get("id") or ""
        links = raw_item.get("links") or {}
        self.link = links.get("self") or ""

    def is_empty(self):
        return not self.id

