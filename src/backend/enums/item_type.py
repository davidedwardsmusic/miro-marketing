from enum import Enum
from dataclasses import dataclass

class ItemType(Enum):
    STICKY_NOTE = "sticky_note"
    TEXT = "text"
    SHAPE = "shape"
    FRAME = "frame"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, item_type: str) -> 'ItemType':
        """
        Create an ItemType from a string value.

        Args:
            item_type: The string representation of the item type (e.g., "sticky_note", "text")

        Returns:
            The corresponding ItemType enum value, or UNKNOWN if not found
        """
        if not item_type:
            return cls.UNKNOWN

        # Normalize to lowercase for comparison
        normalized = item_type.lower().strip()

        # Try to find matching enum value
        for item in cls:
            if item.value == normalized:
                return item

        # Return UNKNOWN if no match found
        return cls.UNKNOWN


