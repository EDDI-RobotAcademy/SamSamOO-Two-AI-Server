from typing import Optional
from datetime import datetime
from enum import Enum


class ReviewPlatform(Enum):
    ELEVENST = "elevenst"
    GMARKET = "gmarket"

    @classmethod
    def from_string(cls, value: str):
        if value is None:
            raise ValueError("ReviewPlatform 값이 None일 수 없습니다.")
        value = value.lower()

        for member in cls:
            if member.value == value:
                return member

        raise ValueError(f"유효하지 않은 ReviewPlatform 값: {value}")


class Review:
    """
    리뷰 도메인 모델 (Domain Entity)
    - id 제거 → (product_id + platform) 복합키로 대체
    """

    def __init__(
        self,
        product_id: str,                        # 플랫폼/서비스에서 관리하는 상품 고유 ID
        platform: ReviewPlatform | str,         # 리뷰가 수집된 플랫폼 (ENUM)
        content: str,                           # 리뷰 본문

        reviewer: Optional[str] = None,         # 리뷰 작성자
        rating: Optional[float] = None,         # 평점 (0~5)
        review_at: Optional[datetime] = None,   # 리뷰가 실제 작성된 시간
        collected_at: Optional[datetime] = None # 시스템이 리뷰를 수집한 시간
    ):

        # 문자열 -> Enum 자동 변환
        if isinstance(platform, str):
            platform = ReviewPlatform.from_string(platform)

        # 복합키 구성요소 (id 없음)
        self.product_id = str(product_id)
        self.platform = platform

        self.reviewer = reviewer
        self.rating = rating
        self.content = content

        # 기본값 처리
        self.review_at = review_at or datetime.utcnow()
        self.collected_at = collected_at or datetime.utcnow()

    @classmethod
    def create_from_crawler(
        cls,
        product_id: str | int,
        platform: str | ReviewPlatform,
        content: str,
        reviewer: Optional[str] = None,
        rating: Optional[float] = None,
        review_at: Optional[datetime] = None
    ):
        """
        크롤러에서 수집된 데이터를 기반으로 Review 객체 생성
        """
        return cls(
            product_id=product_id,
            platform=platform,
            content=content,
            reviewer=reviewer,
            rating=rating,
            review_at=review_at,
            collected_at=datetime.utcnow(),
        )
