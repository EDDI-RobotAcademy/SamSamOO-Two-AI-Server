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
        # ... (기존 create 로직 유지) ...
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

    # ⭐️ 크롤링 요청을 위한 새로운 팩토리 메서드 추가 ⭐️
    @classmethod
    def create_for_crawl_request(cls, platform: str, product_id: str) -> "Product":
        """
        크롤링 요청 시점에 필요한 최소 정보(platform, product_id)만으로
        Product 엔티티를 생성합니다. 나머지 필수 필드는 임시 값으로 채웁니다.
        """
        return cls(
            source=platform,
            source_product_id=product_id,
            title="TEMP_CRAWL_TARGET",
            source_url="",
            seller_id=0,  # int 필수이므로 0 사용
            price=0,  # Optional이나 0으로 설정
            status=ProductStatus.ACTIVE,  # ACTIVE 또는 임시 상태 사용
            registered_at=datetime.utcnow(),
            collected_at=datetime.utcnow()
        )