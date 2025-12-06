from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProductResponse(BaseModel):
    id: int
    source: str
    item_code: str
    title: str
    price: Optional[int]
    seller: Optional[str]
    rating: Optional[float]
    review_count: int
    url: str
    collected_at: datetime
