from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from review.domain.entity.review import ReviewPlatform


class CollectReviewsRequest(BaseModel):
    """리뷰 수집 요청 DTO"""
    platform: ReviewPlatform  # ⭐️ Enum 타입
    product_id: str


class CollectionStatusResponse(BaseModel):
    """수집 상태 응답 DTO"""
    product_id: str
    status: str
    progress: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    total_reviews: Optional[int] = None