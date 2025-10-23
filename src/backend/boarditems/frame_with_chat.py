from dataclasses import dataclass

from src.backend.boarditems.chat_frame import ChatFrame
from src.backend.boarditems.frame import Frame
from src.backend.miro_api import MiroApiClient


@dataclass
class FrameWithChat:
    frame: Frame = None
    chat: ChatFrame = None

    def __init__(self, x: int, y: int, width: int, height: int, fill_color: str, title: str):
        self.frame = Frame(x=x, y=y, width=width, height=height, fill_color=fill_color, title=title)
        frame_for_chat = Frame(x=self.frame.x+30, y=100, width=700, height=280,
                               fill_color="#F8F9FA",
                               title=self.frame.title + ' Chat')
        self.chat = ChatFrame(frame=frame_for_chat)

    def push_to_miro(self) -> str:
        api = MiroApiClient()
        self.frame.push_to_miro()
        self.chat.push_to_miro()

        return self.frame.id
