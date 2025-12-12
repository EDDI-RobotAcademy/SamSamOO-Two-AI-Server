# dashboard/infrastructure/repository/statistics_repository_impl.py

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
        pass  # ✅ 생성자에서 Session 생성 안 함

    def _get_session(self) -> Session:
        """매번 새 세션 반환"""
        return get_db_session()

    def get_platform_distribution(self, seller_id: int) -> List[PlatformStatistics]:
        """플랫폼별 상품 분포 조회"""
        
        db = self._get_session()  # ✅ 변경
        
        try:
            query = (
                select(
                    ProductORM.source,
                    func.count(ProductORM.source_product_id).label("count")
                )
                .where(ProductORM.seller_id == seller_id)
                .group_by(ProductORM.source)
            )

            results = db.execute(query).all()  # ✅ self.db → db
            total = sum(row.count for row in results)

            if total == 0:
                return []

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

            statistics.sort(key=lambda x: x.count, reverse=True)
            return statistics
            
        finally:
            db.close()  # ✅ 추가

    def get_category_distribution(self, seller_id: int) -> List[CategoryStatistics]:
        """카테고리별 상품 분포 조회"""
        
        db = self._get_session()  # ✅ 변경
        
        try:
            query = (
                select(
                    ProductORM.category,
                    func.count(ProductORM.source_product_id).label("count")
                )
                .where(ProductORM.seller_id == seller_id)
                .group_by(ProductORM.category)
            )

            results = db.execute(query).all()  # ✅ self.db → db
            total = sum(row.count for row in results)

            if total == 0:
                return []

            statistics = []
            for row in results:
                percentage = round((row.count / total) * 100, 1)
                statistics.append(
                    CategoryStatistics(
                        category=row.category or "ETC",
                        count=row.count,
                        percentage=percentage
                    )
                )

            statistics.sort(key=lambda x: x.count, reverse=True)
            return statistics
            
        finally:
            db.close()  # ✅ 추가

    def get_total_product_count(self, seller_id: int) -> int:
        """전체 상품 개수 조회"""
        
        db = self._get_session()  # ✅ 변경
        
        try:
            query = (
                select(func.count(ProductORM.source_product_id))
                .where(ProductORM.seller_id == seller_id)
            )
            result = db.execute(query).scalar()  # ✅ self.db → db
            return result or 0
            
        finally:
            db.close()  # ✅ 추가