from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class ReviewItem(BaseModel):
    reviewer: Optional[str]
    rating: Optional[float]
    content: str
    review_at: datetime


class ReviewFetchResponse(BaseModel):
    product_name: str
    platform: str
    product_id: int
    review_count: int
    reviews: List[ReviewItem]
