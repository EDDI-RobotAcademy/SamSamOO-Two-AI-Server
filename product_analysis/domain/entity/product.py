from typing import Optional
from datetime import datetime
from enum import Enum


class Platform(Enum):
    ELEVENST = "elevenst"
    GMARKET = "gmarket"

    @classmethod
    def from_string(cls, value: str):
        if value is None:
            raise ValueError("Platform 값이 None일 수 없습니다.")
        value = value.lower()

        for member in cls:
            if member.value == value:
                return member

        raise ValueError(f"유효하지 않은 Platform 값: {value}")


class ProductStatus(Enum):
    ACTIVE = "ACTIVE"
    STOP = "STOP"

    @classmethod
    def from_string(cls, value: str):
        if value is None:
            raise ValueError("ProductStatus 값이 None일 수 없습니다.")
        value = value.upper()

        for member in cls:
            if member.value == value:
                return member

        raise ValueError(f"유효하지 않은 ProductStatus 값: {value}")


class Product:
    def __init__(
            self,
            source: Platform | str,
            source_product_id: str,
            title: str,
            source_url: str,
            seller_id: int,
            price: Optional[int],
            status: ProductStatus | str,
            registered_at: datetime,

            seller: Optional[str] = None,
            rating: Optional[float] = None,
            review_count: Optional[int] = None,
            collected_at: Optional[datetime] = None,
    ):
        # ------- 🔥 문자열이면 Enum으로 자동 변환 --------
        if isinstance(source, str):
            source = Platform.from_string(source)

        if isinstance(status, str):
            status = ProductStatus.from_string(status)

        self.source = source
        self.status = status
        self.source_product_id = source_product_id
        self.title = title
        self.source_url = source_url
        self.seller_id = seller_id
        self.price = price
        self.registered_at = registered_at

        self.seller = seller
        self.rating = rating
        self.review_count = review_count
        self.collected_at = collected_at

    @classmethod
    def create(
            cls,
            source: Platform | str,
            source_product_id: str,
            title: str,
            source_url: str,
            seller_id: int,
            price: Optional[int] = None,
    ) -> "Product":

        return cls(
            source=source,
            source_product_id=source_product_id,
            title=title,
            source_url=source_url,
            seller_id=seller_id,
            price=price,
            status=ProductStatus.ACTIVE,
            registered_at=datetime.utcnow(),
            collected_at=datetime.utcnow()
        )
