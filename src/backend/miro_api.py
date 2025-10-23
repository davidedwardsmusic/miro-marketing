import json
import os
import urllib.request
import urllib.parse
from http.client import HTTPException
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from src.backend.utils.tag_map import TagMap


class MiroApiError(Exception):
    pass

# Allowed fill colors for sticky notes (as per Miro docs / Web SDK tokens)
ALLOWED_STICKY_FILL_COLORS = {
    "gray",
    "light_yellow", "yellow", "orange",
    "light_green", "green", "dark_green",
    "cyan",
    "light_pink", "pink", "violet", "red",
    "light_blue", "blue", "dark_blue",
    "black",
}
# Allowed text alignment values for sticky notes
ALLOWED_STICKY_TEXT_ALIGN = {"left", "center", "right"}



class MiroApiClient:
    """Lightweight client for Miro REST API v2 using stdlib only.

    Requires MIRO_API_TOKEN (or MIRO_ACCESS_TOKEN/MIRO_TOKEN) in environment (Bearer token).
    """

    def __init__(self) -> None:
        load_dotenv()
        board_id = os.environ.get("MIRO_BOARD_ID")
        self.miro_api_token = os.environ.get("MIRO_API_TOKEN")
        self.board_url = f"https://api.miro.com/v2/boards/{board_id}"

    def change_sticky_note_color(self, id: str, fill_color: str):
        if not fill_color:
            raise Exception("No fill_color specified")

        self._validate_fill_color(fill_color)
        url = f"{self._sticky_notes_url()}/{id}"
        payload: Dict[str, Any] = {"style": {"fillColor": fill_color}}
        return self.request("PATCH", url, payload)

    def create_parented_sticky_note(self, parent_id: str, content: str, x: int, y: int):
        note = self.create_sticky_note(content, 10000, 10000)
        id = note.get("id")
        url = f"{self._sticky_notes_url()}/{id}"
        payload: Dict[str, Any] = {"parent": {"id": parent_id}, "position": {"x": x, "y": y}}
        return self.request("PATCH", url, payload)

    def create_sticky_note(
        self,
        content: str,
        x: int,
        y: int,
        shape: str = "square",
        fill_color: Optional[str] = None,
        text_align: Optional[str] = None,
        width: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a sticky note with minimal payload. Returns created item JSON.
        In v2, content and shape live under the `data` object. Color is optional and
        maps to style.fillColor when provided.

        Allowed fill_color values:
            gray, light_yellow, yellow, orange,
            light_green, green, dark_green,
            cyan,
            light_pink, pink, violet, red,
            light_blue, blue, dark_blue, black

        text_align (optional): one of left, center, right
        width (optional): positive integer dp; if provided, creates note then updates width via PATCH

        Note: The REST API v2 does not support setting width on creation.
        If width is specified, this method creates the note then immediately updates it.

        Example:
            create_sticky_note(
                "Hello",
                shape="rectangle",
                fill_color="light_yellow",
                text_align="left",
                width=500,
            )
        """
        url = self._sticky_notes_url()
        payload: Dict[str, Any] = {"data": {"content": content, "shape": shape}, "position": {"x": x, "y": y}}
        style: Dict[str, Any] = {}
        if fill_color:
            self._validate_fill_color(fill_color)
            style["fillColor"] = fill_color
        if text_align:
            if text_align not in ALLOWED_STICKY_TEXT_ALIGN:
                allowed = ", ".join(sorted(ALLOWED_STICKY_TEXT_ALIGN))
                raise ValueError(f"Invalid text_align '{text_align}'. Allowed: {allowed}")
            style["textAlign"] = text_align
        if style:
            payload["style"] = style

        # Create the sticky note
        result = self.request("POST", url, payload)

        # If width is specified, update it via PATCH
        if width is not None:
            if not isinstance(width, int) or width <= 0:
                raise ValueError("width must be a positive integer if provided")
            item_id = result.get("id")
            if item_id:
                update_url = f"{url}/{item_id}"
                update_payload = {"width": width}
                result = self.request("PATCH", update_url, update_payload)

        return result

    def create_text_item(
        self,
        content: str,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        font_size: int = 14,
        text_align: str = "left",
        fill_color: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a text item on the board. Returns created item JSON.

        Text items support more styling options than sticky notes, including fontSize.

        Note: The REST API v2 does not support setting width for text items.
        Width is auto-calculated based on content and font size.
        Use a larger font_size if you need the text to take up more space.

        Args:
            content: HTML content for the text item
            x: X coordinate (default 0 = board center)
            y: Y coordinate (default 0 = board center)
            font_size: Font size in dp (default 14)
            text_align: One of left, center, right (default left)
            fill_color: Background color - 6-digit hex code like #f5f5f5, or None for transparent (default None)

        Example:
            create_text_item(
                content="<p>Agent: Hello!</p><p>User:</p>",
                font_size=16,
                text_align="left",
                fill_color="#f5f5f5",
            )
        """
        url = f"{self.board_url}/texts"
        style: Dict[str, Any] = {
            "fontSize": str(font_size),
            "textAlign": text_align,
        }

        # Only include fillColor if it's a valid hex color (not None or "transparent")
        if fill_color and fill_color != "transparent":
            style["fillColor"] = fill_color

        payload: Dict[str, Any] = {
            "data": {"content": content},
            "style": style,
            "position": {"x": x, "y": y},
            "geometry": {"width": width}
        }

        return self.request("POST", url, payload)

    def create_shape(
        self,
        content: str,
        shape: str = "rectangle",
        width: int = 400,
        height: int = 100,
        x: int = 0,
        y: int = 0,
        fill_color: str = "transparent",
        text_align: str = "left",
        font_size: int = 14,
        border_color: str = "#000000",
        border_width: int = 2,
    ) -> Dict[str, Any]:
        """Create a shape item on the board. Returns created item JSON.

        Shapes support width/height control and can contain text content.
        Perfect for creating chat boxes with controlled dimensions.

        Args:
            content: HTML content for the shape
            shape: Shape type (default: rectangle). Options: rectangle, round_rectangle, circle, etc.
            width: Width in dp (default 400)
            height: Height in dp (default 100)
            x: X coordinate (default 0 = board center)
            y: Y coordinate (default 0 = board center)
            fill_color: Background color - hex code or 'transparent' (default transparent)
            text_align: One of left, center, right (default left)
            font_size: Font size in dp (default 14)
            border_color: Border color hex code (default #000000 = black)
            border_width: Border width in dp (default 2)

        Example:
            create_shape(
                content="<p>Agent: Hello!</p><p>User:</p>",
                shape="rectangle",
                width=500,
                height=120,
                fill_color="#ADD8E6",
                text_align="left",
            )
        """
        url = f"{self.board_url}/shapes"
        payload: Dict[str, Any] = {
            "data": {
                "content": content,
                "shape": shape,
            },
            "style": {
                "fillColor": fill_color,
                "fontSize": str(font_size),
                "textAlign": text_align,
                "borderColor": border_color,
                "borderWidth": border_width,
            },
            "geometry": {
                "width": width,
                "height": height,
            },
            "position": {"x": x, "y": y},
        }

        return self.request("POST", url, payload)

    def create_frame(
        self,
        title: str = "",
        width: int = 800,
        height: int = 600,
        x: int = 0,
        y: int = 0,
        fill_color: str = "transparent",
        tags: Optional[List[str]] = ['Dummy'],
    ) -> Dict[str, Any]:
        """Create a frame on the board. Returns created frame JSON.

        Frames are containers that can hold other items (shapes, text, sticky notes, etc).
        They help organize board content and can be used for presentations.

        Args:
            title: Frame title/header (default: empty string)
            width: Width in dp (default 800)
            height: Height in dp (default 600)
            x: X coordinate (default 0 = board center)
            y: Y coordinate (default 0 = board center)
            fill_color: Background color - hex code or 'transparent' (default transparent)

        Returns:
            Dict containing the created frame data including 'id' field

        Example:
            frame = create_frame(
                title="Chat Conversation",
                width=600,
                height=300,
                fill_color="#F0F0F0",
            )
            # Use frame['id'] to add child items to the frame
        """
        url = f"{self.board_url}/frames"
        payload: Dict[str, Any] = {
            "data": {
                "title": title,
            },
            "style": {
                "fillColor": fill_color
            },
            "geometry": {
                "width": width,
                "height": height,
            },
            "position": {"x": x, "y": y},
        }

        result = self.request("POST", url, payload)

        # Keep track of the tags
        if tags:
            TagMap().add_tags_to_item(result.get("id"), tags)

        return result

    def request(self, method: str, url: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url=url, data=data, method=method)
        req.add_header("Accept", "application/json")
        req.add_header("Authorization", f"Bearer {self.miro_api_token}")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                text = resp.read().decode(charset)
                return json.loads(text) if text else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="ignore") if hasattr(e, 'read') else ""
            raise MiroApiError(f"HTTP {e.code} {e.reason}: {detail}") from e
        except urllib.error.URLError as e:
            raise MiroApiError(f"Network error: {e}") from e

    def _items_url(self) -> str:
        return f"{self.board_url}/items"

    def _sticky_notes_url(self) -> str:
        return f"{self.board_url}/sticky_notes"

    def _validate_fill_color(self, fill_color):
        if fill_color not in ALLOWED_STICKY_FILL_COLORS:
            allowed = ", ".join(sorted(ALLOWED_STICKY_FILL_COLORS))
            raise ValueError(f"Invalid fill_color '{fill_color}'. Allowed: {allowed}")

    def load_board(self):

        from src.backend.models.miro_board import MiroBoard
        # Use shared client to perform request
        data = self.request("GET", f"{self._items_url()}?limit=40")

        if data is None:
            # If we cannot verify, do not create
            # Optional: print detail for debugging
            try:
                print('Miro items fetch failed:')
            except Exception:
                pass
            return False

        items = []
        if not isinstance(data, dict):
            raise HTTPException("data is not a Dictionary")

        raw_items = data.get('data')
        if not isinstance(raw_items, list):
            raise HTTPException("raw items should be a list")

        return MiroBoard.create(raw_items)

    def update_text_item(self, text_item_id: str, content: str):
        url = f"{self.board_url}/texts/{text_item_id}"
        payload = {"data": {"content": content}}
        return self.request("PATCH", url, payload)

    def delete_item(self, item_id: str):
        """Delete an item from the board by its ID."""
        url = f"{self._items_url()}/{item_id}"
        return self.request("DELETE", url)

    def create_parented_shape(
        self,
        parent_id: str,
        content: str,
        x: int,
        y: int,
        width: int = 1800,
        height: int = 1800,
        shape: str = "rectangle",
        fill_color: str = "#FFFFFF",
        text_align: str = "left",
        font_size: int = 12,
        border_color: str = "#E0E0E0",
        border_width: int = 1,
    ) -> Dict[str, Any]:
        """Create a shape and parent it to a frame.

        Args:
            parent_id: ID of the parent frame
            content: HTML content for the shape
            x: X coordinate relative to parent
            y: Y coordinate relative to parent
            width: Width in dp (default 1800)
            height: Height in dp (default 1800)
            shape: Shape type (default: rectangle)
            fill_color: Background color hex code (default: white)
            text_align: Text alignment (default: left)
            font_size: Font size in dp (default: 12)
            border_color: Border color hex code (default: light gray)
            border_width: Border width in dp (default: 1)

        Returns:
            Dict containing the created and parented shape data
        """
        # Create the shape at a temporary position
        shape_data = self.create_shape(
            content=content,
            shape=shape,
            width=width,
            height=height,
            x=10000,  # Temporary position
            y=10000,
            fill_color=fill_color,
            text_align=text_align,
            font_size=font_size,
            border_color=border_color,
            border_width=border_width,
        )

        # Parent it to the frame and set the correct position
        shape_id = shape_data.get("id")
        url = f"{self.board_url}/shapes/{shape_id}"
        payload: Dict[str, Any] = {
            "parent": {"id": parent_id},
            "position": {"x": x + width/2, "y": y + height/2},
        }
        result = self.request("PATCH", url, payload)
        return result;


