from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import random
from typing import TYPE_CHECKING

from prompt_toolkit.data_structures import Point

from src.backend.enums.item_type import ItemType
from src.backend.models.item_data import ItemData
from src.backend.models.item_geometry import ItemGeometry
from src.backend.models.item_id_and_link import ItemIdAndLink, ItemIdType
from src.backend.models.item_links import ItemLinks
from src.backend.models.item_position import ItemPosition
from src.backend.models.miro_actor import MiroActor
from src.backend.utils.miro_utils import to_datetime

if TYPE_CHECKING:
    from src.backend.models.miro_board import MiroBoard


@dataclass
class MiroItem:
    id: str
    link: str
    parent_id: str
    parent_link: str
    type: ItemType
    data: ItemData
    style: dict
    geometry: ItemGeometry
    position: ItemPosition
    created_at: datetime | None
    created_by: MiroActor
    modified_at: datetime | None
    modified_by: MiroActor
    children: list[str]
    tags: set[str]
    board: MiroBoard

    def __init__(self, raw_item: dict, board: MiroBoard):
        self.parse_raw_item(raw_item)
        self.board = board

    def contains_text(self, text):
        content = self.get_content()
        if not content or not text:
            return False

        return text.lower() in content.lower()

    def get_content(self):
        return self.data.content

    def parse_raw_item(self, raw_item):

        id_and_link = ItemIdAndLink(raw_item, ItemIdType.SELF)
        self.id = id_and_link.id
        self.link = id_and_link.link

        id_and_link = ItemIdAndLink(raw_item, ItemIdType.PARENT)
        self.parent_id = id_and_link.id
        self.parent_link = id_and_link.link

        self.type = ItemType.from_string(raw_item.get('type') or '')
        self.data = ItemData(raw_item.get('data') or {})
        self.style = raw_item.get('style') or {}
        self.geometry = ItemGeometry(raw_item.get('geometry') or {})
        self.position = ItemPosition(raw_item.get('position') or {})
        self.created_at = to_datetime(raw_item.get('createdAt') or '')
        self.created_by = MiroActor(raw_item.get('createdBy') or {})
        self.modified_at = to_datetime(raw_item.get('modifiedAt') or '')
        self.modified_by = MiroActor(raw_item.get('modifiedBy') or {})
        self.tags = set()

    def tags_to_str(self):
        if not self.tags:
            return ""
        return ", ".join(sorted(self.tags))

    def to_dict(self) -> dict:
        """Convert the item to a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "data": self.data.to_dict(),
            "tags": self.tags_to_str(),
            "children": [child.to_dict() for child in self.get_children()]
        }

    def get_children(self):
        return [self.board.get(child_id) for child_id in self.children]

    def __eq__(self, other):
        """Compare items based on key fields, excluding board reference to avoid circular comparison."""
        if not isinstance(other, MiroItem):
            return False

        return (self.id == other.id and
                self.type == other.type and
                self.parent_id == other.parent_id and
                self.get_content() == other.get_content() and
                self.tags == other.tags and
                self.children == other.children)

    def get_descendant_ids(self) -> set[str]:
        """Get all descendant item IDs recursively."""
        descendants = set(self.children)
        for child in self.get_children():
            descendants |= child.get_descendant_ids()
        return descendants

    def is_chat(self):
        return any("chat" in tag.lower() for tag in self.tags)

    # Look through the positions of the child stickies and find the next available position
    def get_next_available_sticky_position(self) -> Point:
        x = random.randint(200, 1000)
        y = random.randint(700,1500)
        return Point(x, y)

    def dump_sticky_notes(self) -> str:
        notes = self.get_sticky_notes()
        notes_map = {note.id: note.get_content() for note in notes}
        result = json.dumps(notes_map)
        return result

    def get_sticky_notes(self):
        return [item for item in self.get_children() if item.type == ItemType.STICKY_NOTE]
