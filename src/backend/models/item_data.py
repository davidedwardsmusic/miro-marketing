from dataclasses import dataclass


@dataclass
class ItemData:
    format: str
    content: str
    show_content: bool
    title: str
    type: str

    def __init__(self, raw_data: dict):
        self.format = raw_data.get("format")
        self.show_content = raw_data.get("showContent")
        self.title = raw_data.get("title")
        self.type = raw_data.get("type")
        self.content = raw_data.get("content")

    def to_dict(self) -> dict:
        """Convert to a JSON-serializable dictionary."""
        return {
            "format": self.format,
            "content": self.content,
            "show_content": self.show_content,
            "title": self.title,
            "type": self.type,
        }

