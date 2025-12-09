"""
대시보드 통계 도메인 엔티티
"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class PlatformStatistics:
    """플랫폼별 상품 통계"""
    platform: str
    count: int
    percentage: float


@dataclass
class CategoryStatistics:
    """카테고리별 상품 통계"""
    category: str
    count: int
    percentage: float


class DashboardStatistics:
    """대시보드 전체 통계"""

    def __init__(
        self,
        platform_distribution: Dict[str, Dict[str, any]],
        category_distribution: Dict[str, Dict[str, any]],
        total_products: int
    ):
        self.platform_distribution = platform_distribution
        self.category_distribution = category_distribution
        self.total_products = total_products

    @classmethod
    def create(
        cls,
        platform_stats: list,
        category_stats: list,
        total: int
    ) -> "DashboardStatistics":
        """통계 객체 생성"""

        platform_dist = {
            stat.platform: {
                "count": stat.count,
                "percentage": stat.percentage
            }
            for stat in platform_stats
        }

        category_dist = {
            stat.category: {
                "count": stat.count,
                "percentage": stat.percentage
            }
            for stat in category_stats
        }

        return cls(
            platform_distribution=platform_dist,
            category_distribution=category_dist,
            total_products=total
        )