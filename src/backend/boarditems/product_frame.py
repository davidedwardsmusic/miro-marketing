from dataclasses import dataclass

from src.backend.boarditems.frame import Frame
from src.backend.miro_api import MiroApiClient


@dataclass
class ProductFrame:
    frame: Frame = None
    product_name: str = ''
    product_description: str = ''
    api: MiroApiClient = None

    def __init__(self, frame: Frame,
                 product_name: str = '',
                 product_description: str = '',
                 tag: str = ''):
        self.frame = frame
        self.api = MiroApiClient()
        self.set_content(product_name, product_description)
        self.tag = tag

    def set_content(self, product_name: str, product_description: str):
        self.product_name = product_name
        self.product_description = product_description

    def push_to_miro(self):
        self.frame.push_to_miro()
