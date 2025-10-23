from dataclasses import dataclass

from src.backend.boarditems.frame import Frame
from src.backend.boarditems.bounds import Bounds
from src.backend.miro_api import MiroApiClient


@dataclass
class ChatFrame:
    frame: Frame = None
    agent_content: str = ''
    user_content: str = ''
    api: MiroApiClient = None

    def __init__(self, frame: Frame,
                 agent_content: str = '',
                 user_content: str = ''):
        self.api = MiroApiClient()
        self.set_content(agent_content, user_content)
        self.frame = frame

    def set_content(self, agent: str, user: str):
        self.agent_content = agent
        self.user_content = user

    def populate(self, agent: str, user: str):
        self.set_content(agent, user)

    def push_to_miro(self) -> str:
        self.frame.push_to_miro()
        top_margin = 0  # Reduced top margin
        left_margin = 30  # Left margin from frame edge
        font_size = 20

        shape_height = 100
        shape_width = 640
        label_height = 50
        label1_bounds = Bounds(left_margin, top_margin, shape_width, label_height)
        label2_bounds = Bounds(left_margin, label1_bounds.y + 100, shape_width, label_height)
        shape_bounds = Bounds(left_margin, label2_bounds.y + 50, shape_width, shape_height)

        label1 = self.api.create_text_item(
            content=f"<p><strong>Agent: </strong></p>{self.agent_content}",
            x=100000,
            y=100000,
            width=shape_width,
            font_size=font_size,
            text_align="left",
        )

        label2 = self.api.create_text_item(
            content="<p><strong>User:</strong></p>",
            x=100000,
            y=100000,
            width=shape_width,
            font_size=font_size,
            text_align="left",
        )

        user_shape = self.api.create_shape(
            content=f"{self.user_content}",
            shape="rectangle",
            width=shape_width,
            height=shape_height,
            x=100000,
            y=100000,
            font_size=font_size,
            text_align="left",
            fill_color="#F5FAFF",
            border_color="#ADD8E6",
            border_width=2,
        )

        # Put the labels and shapes into the frame
        if self.frame.id:
            label1_id = label1.get("id")
            label2_id = label2.get("id")
            user_shape_id = user_shape.get("id")

            # Add label 1 to frame
            if label1_id:
                update_url = f"{self.api._items_url()}/{label1_id}"
                pos = label1_bounds.position()
                self.api.request("PATCH", update_url, {
                    "parent": {"id": self.frame.id},
                    "position": pos
                })

            # Add label 2 to frame
            if label2_id:
                update_url = f"{self.api._items_url()}/{label2_id}"
                self.api.request("PATCH", update_url, {
                    "parent": {"id": self.frame.id},
                    "position": label2_bounds.position()
                })

            # Add user shape to frame
            if user_shape_id:
                update_url = f"{self.api._items_url()}/{user_shape_id}"
                self.api.request("PATCH", update_url, {
                    "parent": {"id": self.frame.id},
                    "position": shape_bounds.position()
                })

            return self.frame.id
