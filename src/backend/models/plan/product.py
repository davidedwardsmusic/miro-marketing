from pydantic import BaseModel


class Product(BaseModel):
    name: str
    description: str
    problem: str
    unique_value_proposition: str
    goals: list[str]
