from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class CrawlingStatusEnum(str, Enum):
    IDLE = "idle"
    COLLECTING = "collecting"
    COMPLETED = "completed"
    ANALYZING = "analyzing"
    DONE = "done"
    FAILED = "failed"


@dataclass
class CrawlingStatus:
    """크롤링 상태 엔티티"""
    product_id: str
    status: CrawlingStatusEnum
    progress: int  # 0-100
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    total_reviews: Optional[int] = None

    @staticmethod
    def create_new(product_id: str) -> 'CrawlingStatus':
        """새로운 크롤링 상태 생성"""
        return CrawlingStatus(
            product_id=product_id,
            status=CrawlingStatusEnum.IDLE,
            progress=0,
            started_at=None,
            completed_at=None
        )

    def start_collecting(self) -> None:
        """수집 시작"""
        self.status = CrawlingStatusEnum.COLLECTING
        self.progress = 0
        self.started_at = datetime.utcnow()
        self.error_message = None

    def update_progress(self, progress: int) -> None:
        """진행률 업데이트"""
        if not 0 <= progress <= 100:
            raise ValueError("진행률은 0-100 사이여야 합니다")
        self.progress = progress

    def complete_collecting(self, total_reviews: int) -> None:
        """수집 완료"""
        self.status = CrawlingStatusEnum.COMPLETED
        self.progress = 100
        self.total_reviews = total_reviews

    def start_analyzing(self) -> None:
        """분석 시작"""
        self.status = CrawlingStatusEnum.ANALYZING
        self.progress = 0

    def complete_analyzing(self) -> None:
        """분석 완료"""
        self.status = CrawlingStatusEnum.DONE
        self.progress = 100
        self.completed_at = datetime.utcnow()

    def mark_failed(self, error_message: str) -> None:
        """실패 처리"""
        self.status = CrawlingStatusEnum.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()

    def can_start_collecting(self) -> bool:
        """수집 시작 가능 여부"""
        return self.status in [
            CrawlingStatusEnum.IDLE,
            CrawlingStatusEnum.FAILED,
            CrawlingStatusEnum.DONE
        ]

    def can_start_analyzing(self) -> bool:
        """분석 시작 가능 여부"""
        return self.status == CrawlingStatusEnum.COMPLETED