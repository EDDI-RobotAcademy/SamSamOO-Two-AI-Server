from abc import ABC, abstractmethod
from typing import Optional
from review.domain.entity.crawling_status import CrawlingStatus

class CrawlingStatusPort(ABC):
    """크롤링 상태 저장소 Port (도메인 인터페이스)"""

    @abstractmethod
    def save(self, status: CrawlingStatus) -> None:
        """product_id 기준 upsert"""
        raise NotImplementedError

    @abstractmethod
    def find_by_product_id(self, product_id: str) -> Optional[CrawlingStatus]:
        """product_id의 최신 상태(없으면 None)"""
        raise NotImplementedError

    @abstractmethod
    def find_latest_by_product_id(self, product_id: str) -> Optional[CrawlingStatus]:
        """명시적 alias (이력 테이블 운영 시 구분 용)"""
        raise NotImplementedError
