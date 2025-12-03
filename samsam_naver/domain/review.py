from pydantic import BaseModel

class Review(BaseModel):
    rating: int
    user: str
    date: str
    text: str
    image: str | None = None
