from pydantic import BaseModel


class Channel(BaseModel):
    name: str
    description: str
