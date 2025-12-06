from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

class AnalysisResponse(BaseModel):
    product_id: int
    pos_count: int
    neg_count: int
    neu_count: int
    top_keywords: Dict[str, int]
    avg_rating: Optional[float]
    analyzed_at: datetime
