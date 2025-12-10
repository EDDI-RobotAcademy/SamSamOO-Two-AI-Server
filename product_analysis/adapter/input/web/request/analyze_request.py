from typing import Optional
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    source: str = Field(..., description="리뷰 출처 (예: '쿠팡', '11번가')")
    source_product_id: str = Field(..., description="출처별 상품 고유 ID")
    limit: Optional[int] = Field(100, description="최대 분석 리뷰 수")