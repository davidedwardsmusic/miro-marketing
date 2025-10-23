import json
from dataclasses import dataclass, field

from src.backend.enums.item_type import ItemType
from src.backend.miro_api import MiroApiClient
from src.backend.models.miro_item import MiroItem
from src.backend.utils.tag_map import TagMap


@dataclass
class MiroBoard:
    items: dict[str, MiroItem] = field(default_factory=dict)
    root_items: list[MiroItem] = field(default_factory=list)

    def clear_user_responses(self):
        """Clear the content of all shapes on the board."""
        api = MiroApiClient()

        # Clear content for each chat shape
        for shape in self.get_chat_shapes():
            if not shape.data.content:
                continue

            shape_id = shape.id
            update_url = f"{api.board_url}/shapes/{shape_id}"
            payload = {
                "data": {
                    "content": ""
                }
            }
            try:
                api.request("PATCH", update_url, payload)
                print(f"Cleared content for shape {shape_id}")
            except Exception as e:
                print(f"Error clearing shape {shape_id}: {e}")
                
    def has_changes_made_note(self):
        return any(item.contains_text("changes made") for item in self.items.values())

    def is_empty(self):
        return len(self.items) == 0

    def get_lowest_changed_items(self):
        pass

    def get_frames(self):
        return [item for item in self.items.values() if item.type == ItemType.FRAME]

    def get_frame_by_tag(self, tag: str) -> MiroItem | None:
        for item in self.get_frames():
            if tag in item.tags:
                return item

        return None

    def add_sticky_note(self, frame_tag: str, content: str, x: int, y: int):
        api = MiroApiClient()
        frame = self.get_frame_by_tag(frame_tag)
        if frame:
            api.create_parented_sticky_note(frame.id, content, x, y)

    def set_agent_prompt(self, chat_frame_tag: str, prompt: str):
        api = MiroApiClient()
        frame = self.get_frame_by_tag(chat_frame_tag)

        if frame:
            prompt_id = self.get_chat_agent_prompt_id(frame)
            if prompt_id:
                final_prompt = f"<p><strong>Agent: </strong></p>{prompt}"
                api.update_text_item(prompt_id, final_prompt)

    def populate_relationships(self):
        """
        This does two things:
        - populates the child ids for each item
        - sets the root items (items with parent_id empty)
        :return:
        """
        # Initialize children list and root_items list
        self.root_items = []
        for item in self.items.values():
            item.children = []

        # Populate children lists and find root items
        for item in self.items.values():
            # If item has no parent_id, it's a root item
            if not item.parent_id:
                self.root_items.append(item)
            else:
                # Add this item to its parent's children list
                parent = self.get(item.parent_id)
                if parent:
                    parent.children.append(item.id)

        # Populate the tags
        tags = TagMap().get_map()
        for tag, item_ids in tags.items():
            for item_id in item_ids:
                item = self.get(item_id)
                if item:
                    item.tags.add(tag)

    def get(self, item_id: str) -> MiroItem | None:
        return self.items.get(item_id)

    @classmethod
    def create(cls, raw_items) -> "MiroBoard":
        board = cls()
        item_list = [MiroItem(item, board) for item in raw_items]
        items = {item.id: item for item in item_list}

        board.set_items(items)
        return board

    def to_dict(self) -> dict:
        """Convert the board to a JSON-serializable dictionary."""
        map = {}
        for root in self.root_items:
            map[f"{root.id}_{root.tags_to_str()}"] = root.to_dict()

        return map

    def chat_to_text(self, chat: dict) -> str:
        result = ''
        children = chat['children']
        result = f"{children[0]['data']['content']}\nUser: {children[2]['data']['content']}"
        return result

    def is_set_up(self) -> bool:
        return len(self.root_items) > 1

    def to_json_for_llm(self) -> str:
        map = {}
        chats: dict = self.chats_to_dict()
        for k,v in chats.items():
            map[k] = self.chat_to_text(v)

        return json.dumps(map, ensure_ascii=False, indent=2)

    def get_chat_frames(self) -> list[MiroItem]:
        frames = []
        for root in self.root_items:
            if root.is_chat():
                frames.append(root)

        return frames

    def get_chat_agent_prompt_id(self, chat_frame: MiroItem) -> str | None:
        return chat_frame.get_children()[0].id

    def chats_to_dict(self) -> dict:
        """Convert the board to a JSON-serializable dictionary."""
        map = {}
        for chat in self.get_chat_frames():
            map[f"{chat.id}_{chat.tags_to_str()}"] = chat.to_dict()

        return map

    def set_items(self, items):
        self.items = items
        self.populate_relationships()

    def __eq__(self, other):
        """Compare boards based on their items."""
        if not isinstance(other, MiroBoard):
            return False

        # Compare the set of item IDs
        if set(self.items.keys()) != set(other.items.keys()):
            return False

        # Delegate item comparison to MiroItem.__eq__
        for item_id in self.items.keys():
            if self.items[item_id] != other.items[item_id]:
                return False

        return True

    def get_segment_frame(self):
        return self.get_frame_by_tag('Segments')

    def get_product_frame(self):
        return self.get_frame_by_tag('Product')

    def get_channels_frame(self):
        return self.get_frame_by_tag('Channels')

    def get_summary_frame(self):
        return self.get_frame_by_tag('Summary')

    def get_chat_shapes(self):
        """Get all shapes that are children of chat frames."""
        shapes = []
        for frame in self.get_chat_frames():
            for child in frame.get_children():
                if child.type == ItemType.SHAPE:
                    shapes.append(child)

        return shapes




