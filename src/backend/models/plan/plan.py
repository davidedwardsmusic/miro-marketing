from pydantic import BaseModel

from src.backend.models.plan.channel import Channel
from src.backend.models.plan.product import Product
from src.backend.models.plan.segment import Segment
from src.backend.models.plan.suggestion import Suggestion


class Plan(BaseModel):
    product: Product
    segments: list[Segment]
    channels: list[Channel]
    suggestions: list[Suggestion]
