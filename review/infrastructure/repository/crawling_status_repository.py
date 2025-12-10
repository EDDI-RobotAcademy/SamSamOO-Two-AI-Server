from abc import ABC, abstractmethod
from typing import Optional
from review.domain.entity.crawling_status import CrawlingStatus


class CrawlingStatusRepository(ABC):
    """크롤링 상태 저장소 인터페이스"""

    @abstractmethod
    def save(self, status: CrawlingStatus) -> None:
        """상태 저장"""
        pass

    @abstractmethod
    def find_by_product_id(self, product_id: str) -> Optional[CrawlingStatus]:
        """상품 ID로 상태 조회"""
        pass

    @abstractmethod
    def find_latest_by_product_id(self, product_id: str) -> Optional[CrawlingStatus]:
        """가장 최근 상태 조회 (이력 관리 시)"""
        pass