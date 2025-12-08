from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict

@dataclass
class AnalysisResult:
    id: Optional[int]
    product_id: int
    pos_count: int
    neg_count: int
    neu_count: int
    top_keywords: Dict[str, int]
    avg_rating: Optional[float]
    analyzed_at: datetime
