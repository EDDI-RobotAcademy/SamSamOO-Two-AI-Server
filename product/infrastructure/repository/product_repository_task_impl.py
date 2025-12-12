# product/infrastructure/repository/product_repository_task_impl.py
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import update as sa_update

from product.domain.entity.product import (
    Product, Platform, ProductStatus, ProductCategory, AnalysisStatus
)
from product.infrastructure.orm.product_orm import ProductORM

def _to_enum_value(value, enum_cls):
    if isinstance(value, enum_cls):
        return value.value
    return enum_cls.from_string(value).value

class ProductRepositoryTaskImpl:
    """
    Celery 태스크 전용 구현.
    - 외부에서 전달된 Session(self.db)만 사용
    - commit/rollback/close 절대 수행하지 않음 (트랜잭션 책임 = 태스크)
    """
    def __init__(self, session: Session):
        self.db = session

    def find_by_composite_key(
        self, source: Platform | str, source_product_id: str
    ) -> Optional[Product]:
        source_value = _to_enum_value(source, Platform)
        orm = (
            self.db.query(ProductORM)
            .filter(
                ProductORM.source == source_value,
                ProductORM.source_product_id == source_product_id,
            )
            .one_or_none()
        )
        if not orm:
            return None
        return Product(
            source=Platform.from_string(orm.source),
            source_product_id=orm.source_product_id,
            title=orm.title,
            price=orm.price,
            seller=orm.seller,
            rating=orm.rating,
            review_count=orm.review_count,
            source_url=orm.url,
            status=ProductStatus.from_string(orm.status),
            seller_id=orm.seller_id,
            collected_at=orm.collected_at,
            registered_at=orm.collected_at,
            category=ProductCategory.from_string(orm.category),
            analysis_status=AnalysisStatus.from_string(orm.analysis_status),
        )

    def update_analysis_status(
        self,
        source: Platform | str,
        source_product_id: str,
        status: AnalysisStatus | str,
    ) -> None:
        source_value = _to_enum_value(source, Platform)
        status_value = _to_enum_value(status, AnalysisStatus)
        stmt = (
            sa_update(ProductORM)
            .where(
                ProductORM.source == source_value,
                ProductORM.source_product_id == source_product_id,
            )
            .values(analysis_status=status_value)
        )
        self.db.execute(stmt)
        # 커밋은 태스크에서!
