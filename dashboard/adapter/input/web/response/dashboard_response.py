"""
대시보드 통계 응답 DTO
"""
from pydantic import BaseModel, Field
from typing import Dict, Optional


class PlatformDistributionItem(BaseModel):
    """플랫폼별 분포 항목"""
    count: int = Field(..., description="상품 개수")
    percentage: float = Field(..., description="비율 (%)")


class CategoryDistributionItem(BaseModel):
    """카테고리별 분포 항목"""
    count: int = Field(..., description="상품 개수")
    percentage: float = Field(..., description="비율 (%)")


class DashboardStatisticsResponse(BaseModel):
    """대시보드 전체 통계 응답"""
    platform_distribution: Dict[str, PlatformDistributionItem] = Field(
        default={},  # 기본값 빈 dict
        description="플랫폼별 상품 분포"
    )
    category_distribution: Dict[str, CategoryDistributionItem] = Field(
        default={},  # 기본값 빈 dict
        description="카테고리별 상품 분포"
    )
    total_products: int = Field(default=0, description="전체 상품 수")

    class Config:
        json_schema_extra = {
            "example": {
                "platform_distribution": {
                    "elevenst": {"count": 10, "percentage": 40.0},
                    "lotteon": {"count": 15, "percentage": 60.0}
                },
                "category_distribution": {
                    "FOOD": {"count": 12, "percentage": 48.0},
                    "DIGITAL": {"count": 6, "percentage": 24.0},
                    "ETC": {"count": 7, "percentage": 28.0}
                },
                "total_products": 25
            }
        }


class PlatformDistributionResponse(BaseModel):
    """플랫폼별 분포 응답"""
    elevenst: Optional[PlatformDistributionItem] = Field(None, description="11번가 분포")
    lotteon: Optional[PlatformDistributionItem] = Field(None, description="롯데온 분포")
    danawa: Optional[PlatformDistributionItem] = Field(None, description="다나와 분포")

    class Config:
        json_schema_extra = {
            "example": {
                "elevenst": {"count": 10, "percentage": 40.0},
                "lotteon": {"count": 7, "percentage": 35.0},
                "danawa": {"count": 5, "percentage": 25.0}
            }
        }


class CategoryDistributionResponse(BaseModel):
    """카테고리별 분포 응답"""
    FOOD: Optional[CategoryDistributionItem] = Field(None, description="식품 분포")
    DIGITAL: Optional[CategoryDistributionItem] = Field(None, description="디지털/가전 분포")
    CLOTHING: Optional[CategoryDistributionItem] = Field(None, description="의류 분포")
    ETC: Optional[CategoryDistributionItem] = Field(None, description="기타 분포")

    class Config:
        json_schema_extra = {
            "example": {
                "FOOD": {"count": 12, "percentage": 48.0},
                "DIGITAL": {"count": 6, "percentage": 24.0},
                "ETC": {"count": 7, "percentage": 28.0}
            }
        }