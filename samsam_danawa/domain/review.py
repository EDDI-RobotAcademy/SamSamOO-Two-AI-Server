from pydantic import BaseModel
from typing import Optional

class DanawaReview(BaseModel):
    user: str
    date: str
    text: str
    category: Optional[str] = None
    image: Optional[str] = None
    rating: Optional[int] = None
