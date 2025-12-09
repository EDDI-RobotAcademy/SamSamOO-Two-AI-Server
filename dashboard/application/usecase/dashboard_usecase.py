from dashboard.application.port.statistics_repository_port import StatisticsRepositoryPort
from dashboard.domain.entity.statistics import DashboardStatistics


class DashboardUseCase:

    def __init__(self, statistics_repo: StatisticsRepositoryPort):
        self.statistics_repo = statistics_repo

    def get_dashboard_statistics(self, seller_id: int) -> DashboardStatistics:
        """
        대시보드에 표시할 전체 통계를 조회합니다.

        Args:
            seller_id: 판매자 ID (로그인한 사용자)
        """
        # 플랫폼별 분포 조회
        platform_stats = self.statistics_repo.get_platform_distribution(seller_id)

        # 카테고리별 분포 조회
        category_stats = self.statistics_repo.get_category_distribution(seller_id)

        # 전체 상품 수 조회
        total_products = self.statistics_repo.get_total_product_count(seller_id)

        # DashboardStatistics 객체 생성
        dashboard_stats = DashboardStatistics.create(
            platform_stats=platform_stats,
            category_stats=category_stats,
            total=total_products
        )

        return dashboard_stats

    def get_platform_distribution(self, seller_id: int) -> dict:
        """
        플랫폼별 상품 분포만 조회합니다.

        Args:
            seller_id: 판매자 ID (로그인한 사용자)
        """
        platform_stats = self.statistics_repo.get_platform_distribution(seller_id)

        return {
            stat.platform: {
                "count": stat.count,
                "percentage": stat.percentage
            }
            for stat in platform_stats
        }

    def get_category_distribution(self, seller_id: int) -> dict:
        """
        카테고리별 상품 분포만 조회합니다.

        Args:
            seller_id: 판매자 ID (로그인한 사용자)
        """
        category_stats = self.statistics_repo.get_category_distribution(seller_id)

        return {
            stat.category: {
                "count": stat.count,
                "percentage": stat.percentage
            }
            for stat in category_stats
        }