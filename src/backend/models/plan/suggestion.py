from pydantic import BaseModel


class Suggestion(BaseModel):
    name: str
    description: str
    priority: str
