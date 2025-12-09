from abc import ABC, abstractmethod
from typing import List
from dashboard.domain.entity.statistics import PlatformStatistics, CategoryStatistics


class StatisticsRepositoryPort(ABC):
    """통계 데이터 조회 리포지토리 인터페이스"""

    @abstractmethod
    def get_platform_distribution(self, seller_id: int) -> List[PlatformStatistics]:
        """플랫폼별 상품 분포를 조회합니다."""
        pass

    @abstractmethod
    def get_category_distribution(self, seller_id: int) -> List[CategoryStatistics]:
        """카테고리별 상품 분포를 조회합니다."""
        pass

    @abstractmethod
    def get_total_product_count(self, seller_id: int) -> int:
        """전체 상품 개수를 조회합니다."""
        pass