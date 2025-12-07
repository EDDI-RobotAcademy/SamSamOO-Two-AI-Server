from pydantic import BaseModel, Field
from typing import Optional
from product.domain.entity.product import Platform


class ProductCreateRequest(BaseModel):
    source: Platform = Field(..., description="상품 출처 플랫폼 (Platform Enum)")
    source_product_id: str = Field(..., description="원본 플랫폼에서 부여한 상품 ID/코드 (판매자 필수 입력)")
    title: str = Field(..., description="상품 제목 (검증 후 최종 확정)")
    source_url: str = Field(..., description="상품 상세 URL (검증의 기준)")
    price: Optional[int] = Field(None, description="상품 가격 (선택 사항)")

    class Config:
        use_enum_values = True