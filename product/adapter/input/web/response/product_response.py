from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProductResponse(BaseModel):
    source_product_id: int
    source: str
    title: str
    category: str
    analysis_status: str
    price: Optional[int]
    seller: Optional[str]
    rating: Optional[float]
    review_count: Optional[int] = None
    source_url: str
    collected_at: datetime
