from typing import List, Optional, Callable
from sqlalchemy.orm import Session

from product.domain.entity.product import Product, Platform, ProductStatus, ProductCategory, AnalysisStatus
from product.infrastructure.orm.product_orm import ProductORM
from product.application.port.product_repository_port import ProductRepositoryPort
from config.database.session import get_db_session


def _to_enum_value(value, enum_cls):
    """문자열 입력도 Enum으로 자동 변환"""
    if isinstance(value, enum_cls):
        return value.value
    return enum_cls.from_string(value).value


class ProductRepositoryImpl(ProductRepositoryPort):
    def __init__(self, session_factory: Callable[[], Session] = get_db_session):
        self._session_factory = session_factory

    def _with_session(self):
        db = self._session_factory()
        try:
            yield db
        finally:
            db.close()

    def save(self, product: Product) -> Product:
        for db in self._with_session():
            try:
                orm = ProductORM(
                    source=_to_enum_value(product.source, Platform),
                    source_product_id=product.source_product_id,
                    title=product.title,
                    category=_to_enum_value(product.category, ProductCategory),
                    analysis_status=_to_enum_value(product.analysis_status, AnalysisStatus),
                    price=product.price,
                    seller=product.seller,
                    rating=product.rating,
                    review_count=product.review_count,
                    url=product.source_url,
                    status=_to_enum_value(product.status, ProductStatus),
                    seller_id=product.seller_id,
                    collected_at=product.collected_at,
                )
                db.add(orm)
                db.commit()
                db.refresh(orm)
                return product
            except Exception:
                db.rollback()
                raise

    def update(self, product: Product) -> Product:
        source_value = _to_enum_value(product.source, Platform)
        for db in self._with_session():
            try:
                orm = (
                    db.query(ProductORM)
                    .filter(
                        ProductORM.source == source_value,
                        ProductORM.source_product_id == product.source_product_id,
                    )
                    .one_or_none()
                )
                if not orm:
                    raise ValueError("업데이트 대상 상품 없음")

                orm.title = product.title
                orm.price = product.price
                orm.seller = product.seller
                orm.rating = product.rating
                orm.review_count = product.review_count
                orm.url = product.source_url
                orm.status = _to_enum_value(product.status, ProductStatus)
                orm.seller_id = product.seller_id
                orm.category = _to_enum_value(product.category, ProductCategory)
                orm.analysis_status = _to_enum_value(product.analysis_status, AnalysisStatus)

                db.commit()
                db.refresh(orm)
                return product
            except Exception:
                db.rollback()
                raise

    def delete(self, source: Platform, source_product_id: str) -> bool:
        source_value = _to_enum_value(source, Platform)
        for db in self._with_session():
            try:
                deleted = (
                    db.query(ProductORM)
                    .filter(
                        ProductORM.source == source_value,
                        ProductORM.source_product_id == source_product_id,
                    )
                    .delete(synchronize_session=False)
                )
                db.commit()
                return deleted > 0
            except Exception:
                db.rollback()
                raise

    # ---------- queries ----------
    def find_by_composite_key(self, source: Platform, source_product_id: str) -> Optional[Product]:
        source_value = _to_enum_value(source, Platform)
        for db in self._with_session():
            orm = (
                db.query(ProductORM)
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

    def find_all(self, limit: int = 10) -> List[Product]:
        for db in self._with_session():
            orms = db.query(ProductORM).limit(limit).all()
            return [
                Product(
                    source=Platform.from_string(o.source),
                    source_product_id=o.source_product_id,
                    title=o.title,
                    price=o.price,
                    seller=o.seller,
                    rating=o.rating,
                    review_count=o.review_count,
                    source_url=o.url,
                    status=ProductStatus.from_string(o.status),
                    seller_id=o.seller_id,
                    collected_at=o.collected_at,
                    registered_at=o.collected_at,
                    category=ProductCategory.from_string(o.category),
                    analysis_status=AnalysisStatus.from_string(o.analysis_status),
                )
                for o in orms
            ]

    def find_by_title_like(self, source: Platform, keyword: str) -> List[Product]:
        source_value = _to_enum_value(source, Platform)
        for db in self._with_session():
            # 바인딩 사용 권장
            like = f"%{keyword}%"
            orms = (
                db.query(ProductORM)
                .filter(ProductORM.source == source_value, ProductORM.title.like(like))
                .all()
            )
            return [
                Product(
                    source=Platform.from_string(o.source),
                    source_product_id=o.source_product_id,
                    title=o.title,
                    price=o.price,
                    seller=o.seller,
                    rating=o.rating,
                    review_count=o.review_count,
                    source_url=o.url,
                    status=ProductStatus.from_string(o.status),
                    seller_id=o.seller_id,
                    collected_at=o.collected_at,
                    registered_at=o.collected_at,
                    category=ProductCategory.from_string(o.category),
                    analysis_status=AnalysisStatus.from_string(o.analysis_status),
                )
                for o in orms
            ]
