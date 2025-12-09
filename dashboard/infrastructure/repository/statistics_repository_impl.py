"""
통계 리포지토리 구현
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from typing import List

from product.infrastructure.orm.product_orm import ProductORM
from dashboard.domain.entity.statistics import PlatformStatistics, CategoryStatistics
from dashboard.application.port.statistics_repository_port import StatisticsRepositoryPort
from config.database.session import get_db_session


class StatisticsRepositoryImpl(StatisticsRepositoryPort):
    """통계 데이터 조회 리포지토리 구현"""

    def __init__(self):
        self.db: Session = get_db_session()

    def get_platform_distribution(self, seller_id: int) -> List[PlatformStatistics]:
        """
        플랫폼별 상품 분포를 조회합니다.

        Args:
            seller_id: 판매자 ID (로그인한 사용자)

        Returns:
            List[PlatformStatistics]: 플랫폼별 통계 리스트
        """
        # source 컬럼으로 그룹핑하여 개수 집계 (seller_id 필터 추가)
        query = (
            select(
                ProductORM.source,
                func.count(ProductORM.source_product_id).label("count")
            )
            .where(ProductORM.seller_id == seller_id)
            .group_by(ProductORM.source)
        )

        results = self.db.execute(query).all()

        # 전체 개수 계산
        total = sum(row.count for row in results)

        if total == 0:
            return []

        # PlatformStatistics 객체로 변환
        statistics = []
        for row in results:
            percentage = round((row.count / total) * 100, 1)
            statistics.append(
                PlatformStatistics(
                    platform=row.source,
                    count=row.count,
                    percentage=percentage
                )
            )

        # 개수 기준 내림차순 정렬
        statistics.sort(key=lambda x: x.count, reverse=True)

        return statistics

    def get_category_distribution(self, seller_id: int) -> List[CategoryStatistics]:
        """
        카테고리별 상품 분포를 조회합니다.

        Args:
            seller_id: 판매자 ID (로그인한 사용자)

        Returns:
            List[CategoryStatistics]: 카테고리별 통계 리스트
        """
        # category 컬럼으로 그룹핑하여 개수 집계 (seller_id 필터 추가)
        query = (
            select(
                ProductORM.category,
                func.count(ProductORM.source_product_id).label("count")
            )
            .where(ProductORM.seller_id == seller_id)
            .group_by(ProductORM.category)
        )

        results = self.db.execute(query).all()

        # 전체 개수 계산
        total = sum(row.count for row in results)

        if total == 0:
            return []

        # CategoryStatistics 객체로 변환
        statistics = []
        for row in results:
            percentage = round((row.count / total) * 100, 1)
            statistics.append(
                CategoryStatistics(
                    category=row.category or "ETC",  # NULL인 경우 "ETC"로 표시
                    count=row.count,
                    percentage=percentage
                )
            )

        # 개수 기준 내림차순 정렬
        statistics.sort(key=lambda x: x.count, reverse=True)

        return statistics

    def get_total_product_count(self, seller_id: int) -> int:
        """
        전체 상품 개수를 조회합니다.

        Args:
            seller_id: 판매자 ID (로그인한 사용자)

        Returns:
            int: 전체 상품 수
        """
        # 복합 키이므로 source_product_id 기준으로 count (seller_id 필터 추가)
        query = (
            select(func.count(ProductORM.source_product_id))
            .where(ProductORM.seller_id == seller_id)
        )
        result = self.db.execute(query).scalar()
        return result or 0