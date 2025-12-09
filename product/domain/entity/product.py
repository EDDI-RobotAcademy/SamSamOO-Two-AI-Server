from typing import Optional
from datetime import datetime
from enum import Enum


# --- 새로운 Enum 정의 ---
class ProductCategory(Enum):
    FOOD = "FOOD"
    DIGITAL = "DIGITAL"
    CLOTHING = "CLOTHING"
    ETC = "ETC"

    @classmethod
    def from_string(cls, value: str):
        if value is None:
            raise ValueError("ProductCategory 값이 None일 수 없습니다.")
        value = value.upper()

        for member in cls:
            if member.value == value:
                return member

        raise ValueError(f"유효하지 않은 ProductCategory 값: {value}")


class AnalysisStatus(Enum):
    PENDING = "PENDING"  # 분석 대기 중
    IN_PROGRESS = "IN_PROGRESS"  # 분석 진행 중
    COMPLETED = "COMPLETED"  # 분석 완료
    FAILED = "FAILED"  # 분석 실패

    @classmethod
    def from_string(cls, value: str):
        if value is None:
            raise ValueError("AnalysisStatus 값이 None일 수 없습니다.")
        value = value.upper()

        for member in cls:
            if member.value == value:
                return member

        raise ValueError(f"유효하지 않은 AnalysisStatus 값: {value}")


# --- 기존 Enum 정의 (유지) ---
class Platform(Enum):
    ELEVENST = "elevenst"
    LOTTEON = "lotteon"

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


# --- Product 엔티티 수정 ---
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

            # ⭐️ 새로 추가된 필수 필드 ⭐️
            category: ProductCategory | str,
            analysis_status: AnalysisStatus | str,

            seller: Optional[str] = None,
            rating: Optional[float] = None,
            review_count: Optional[int] = None,
            collected_at: Optional[datetime] = None,
    ):
        if isinstance(source, str):
            source = Platform.from_string(source)

        if isinstance(status, str):
            status = ProductStatus.from_string(status)

        # ⭐️ Enum 변환 로직 추가 ⭐️
        if isinstance(category, str):
            category = ProductCategory.from_string(category)

        if isinstance(analysis_status, str):
            analysis_status = AnalysisStatus.from_string(analysis_status)

        self.source = source
        self.status = status
        self.category = category  # ⭐️ 필드 추가 ⭐️
        self.analysis_status = analysis_status  # ⭐️ 필드 추가 ⭐️
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
            category: ProductCategory | str = ProductCategory.ETC,  # ⭐️ 기본값 ETC 설정 ⭐️
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
            collected_at=datetime.utcnow(),
            category=category,  # ⭐️ 필드 전달 ⭐️
            analysis_status=AnalysisStatus.PENDING  # ⭐️ 기본값 PENDING 설정 ⭐️
        )

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
            seller_id=0,
            price=0,
            status=ProductStatus.ACTIVE,
            registered_at=datetime.utcnow(),
            collected_at=datetime.utcnow(),

            # ⭐️ 크롤링 요청 시점의 기본값 설정 ⭐️
            category=ProductCategory.ETC,
            analysis_status=AnalysisStatus.PENDING
        )