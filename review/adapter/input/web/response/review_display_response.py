from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ReviewDisplayResponse:
    """리뷰 조회용 응답 객체"""
    review_id: int
    reviewer: str
    rating: float
    content: str
    review_at: Optional[datetime]
    collected_at: Optional[datetime]

    @staticmethod
    def from_orm(orm_review):
        """ReviewORM -> ReviewDisplayResponse 변환"""
        return ReviewDisplayResponse(
            review_id=orm_review.review_id,
            reviewer=orm_review.reviewer,
            rating=orm_review.rating,
            content=orm_review.content,
            review_at=orm_review.review_at,
            collected_at=orm_review.collected_at
        )

    def to_dict(self):
        """딕셔너리로 변환 (API 응답용)"""
        return {
            "review_id": self.review_id,
            "reviewer": self.reviewer,
            "rating": self.rating,
            "content": self.content,
            "review_at": self.review_at.isoformat() if self.review_at else None,
            "collected_at": self.collected_at.isoformat() if self.collected_at else None
        }