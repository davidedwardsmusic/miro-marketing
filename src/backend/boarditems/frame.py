from dataclasses import dataclass

from src.backend.miro_api import MiroApiClient


@dataclass
class Frame:
    width: int = 800
    height: int = 600
    x: int = 0
    y: int = 0
    fill_color: str = "transparent"
    title: str = ''
    api: MiroApiClient = MiroApiClient()
    id: str = ''

    def fix_x(self):
        return self.x + (self.width / 2)

    def fix_y(self):
        return self.y + (self.height / 2)

    def rel_x(self):
        return self.x + (self.width / 2)

    def rel_y(self):
        return self.y + (self.height / 2)

    def push_to_miro(self) -> str:
        # Frame dimensions - tighter fit with minimal margins
        frame_width = 700
        frame_height = 250  # Reduced to fit content snugly
        frame_x = 0
        frame_y = 0
        font_size = 20

        # Create a frame to contain the chat shapes
        frame = self.api.create_frame(
            title=self.title,
            width=self.width,
            height=self.height,
            x=self.fix_x(),
            y=self.fix_y(),
            fill_color=self.fill_color,
            tags=[self.title] if self.title else [],
        )

        self.id = frame.get("id")
        return self.id
