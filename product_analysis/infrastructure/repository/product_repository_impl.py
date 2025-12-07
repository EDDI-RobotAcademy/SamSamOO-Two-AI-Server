from typing import List, Optional
from sqlalchemy.orm import Session

from product_analysis.domain.entity.product import Product, Platform, ProductStatus
from product_analysis.infrastructure.orm.product_orm import ProductORM
from product_analysis.application.port.product_repository_port import ProductRepositoryPort
from config.database.session import get_db_session


def _to_enum_value(value, enum_cls):
    """문자열 입력도 Enum으로 자동 변환"""
    if isinstance(value, enum_cls):
        return value.value
    return enum_cls.from_string(value).value


class ProductRepositoryImpl(ProductRepositoryPort):

    def __init__(self):
        self.db: Session = get_db_session()

    def save(self, product: Product) -> Product:

        orm = ProductORM(
            source=_to_enum_value(product.source, Platform),
            source_product_id=product.source_product_id,
            title=product.title,
            price=product.price,
            seller=product.seller,
            rating=product.rating,
            review_count=product.review_count,
            url=product.source_url,
            status=_to_enum_value(product.status, ProductStatus),
            seller_id=product.seller_id,
            collected_at=product.collected_at
        )

        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)

        return product

    def update(self, product: Product) -> Product:

        source_value = _to_enum_value(product.source, Platform)

        orm = self.db.query(ProductORM).filter(
            ProductORM.source == source_value,
            ProductORM.source_product_id == product.source_product_id
        ).one_or_none()

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

        self.db.commit()
        self.db.refresh(orm)

        return product

    def delete(self, source: Platform, source_product_id: str) -> bool:

        source_value = _to_enum_value(source, Platform)

        deleted = self.db.query(ProductORM).filter(
            ProductORM.source == source_value,
            ProductORM.source_product_id == source_product_id
        ).delete()

        self.db.commit()

        return deleted > 0

    def find_by_composite_key(self, source: Platform, source_product_id: str) -> Optional[Product]:
        source_value = _to_enum_value(source, Platform)

        orm = self.db.query(ProductORM).filter(
            ProductORM.source == source_value,
            ProductORM.source_product_id == source_product_id
        ).one_or_none()

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
        )

    def find_all(self, limit: int = 10) -> List[Product]:
        orms = self.db.query(ProductORM).limit(limit).all()
        products = []

        for orm in orms:
            products.append(
                Product(
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
                )
            )

        return products

    def find_by_title_like(self, source: Platform, keyword: str) -> List[Product]:

        source_value = _to_enum_value(source, Platform)

        orms = self.db.query(ProductORM).filter(
            ProductORM.source == source_value,
            ProductORM.title.like(f"%{keyword}%")
        ).all()

        return [
            Product(
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
            )
            for orm in orms
        ]
