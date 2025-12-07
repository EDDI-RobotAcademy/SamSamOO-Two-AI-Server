from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Review:
    id: Optional[int]
    product_id: Optional[int]
    rating: Optional[int]
    content: str
    written_at: Optional[datetime]
    collected_at: datetime
