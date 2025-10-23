from dataclasses import dataclass, field

from src.backend.boarditems.bounds import Bounds
from src.backend.boarditems.frame import Frame
from src.backend.boarditems.frame_with_chat import FrameWithChat

FRAME_WIDTH = 2000
FRAME_HEIGHT = 2000

@dataclass
class FrameDefinitions:
    chat: Frame = None
    product: FrameWithChat = None
    segments: FrameWithChat = None
    channels: FrameWithChat = None
    summary: FrameWithChat = None

    def __init__(self):
        self.chat = Frame(x=-800, y=100, width=700, height=280,
                          fill_color="#F8F9FA",
                          title='Initial Chat')
        width = 1000
        height = 2000
        x = 0
        self.product = FrameWithChat(x=x, y=0, width=width, height=height,
                                     fill_color="#F5FAFF",
                                     title='Product')
        x += width
        self.segments = FrameWithChat(x=x, y=0, width=width, height=height,
                                      fill_color="#EBF5FF",
                                      title='Segments')
        x += width
        self.channels = FrameWithChat(x=x, y=0, width=width, height=height,
                                      fill_color="#E6F7FF",
                                      title='Channels')
        x += width
        self.summary = FrameWithChat(x=x, y=0, width=width, height=height,
                                     fill_color="#E0F2FF",
                                     title='Summary')
