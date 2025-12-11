from pydantic import BaseModel, Field

class ReviewReanalyzeRequest(BaseModel):
    source: str = Field(..., description="예: elevenst, gmarket, lotteon")
    product_id: str = Field(..., description="플랫폼별 상품 ID 문자열")
    # 필요 시 재분석 전에 이전 분석 결과를 정리할지 옵션 (태스크 내부에서 사용)
    clear_previous: bool = Field(default=True, description="기존 분석/인사이트 삭제 여부")
