from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Product:
    id: Optional[int]
    source: str              # 'gmarket' | 'naver' | 'coupang'
    item_code: str
    title: str
    price: Optional[int]
    seller: Optional[str]
    rating: Optional[float]
    review_count: int
    url: str
    collected_at: datetime
