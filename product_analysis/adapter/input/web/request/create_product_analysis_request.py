from pydantic import BaseModel, Field
from enum import Enum

class Provider(str, Enum):
    elevenst = "elevenst"
    lotteon = "lotteon"
    # naver = "naver"
    # coupang = "coupang"

class CreateProductAnalysisRequest(BaseModel):
    provider: Provider = Field(..., description="데이터 소스")
    keyword: str = Field(..., min_length=1)
    limit_products: int = 5
    limit_reviews: int = 20
