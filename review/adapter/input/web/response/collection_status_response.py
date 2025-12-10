from pydantic import BaseModel
from typing import Optional


class CollectionStatusResponse(BaseModel):
    """프론트엔드 폴링 로직이 기대하는 상태 응답 모델"""
    status: str

    # 전체 진행도 (0~100)
    progress: Optional[float] = 0.0

    # 수집된 리뷰 총 개수
    total_reviews: Optional[int] = 0

    # 실패 시 표시할 오류 메시지
    error_message: Optional[str] = None