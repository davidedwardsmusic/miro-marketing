from pydantic import BaseModel


class Segment(BaseModel):
    name: str
    description: str
