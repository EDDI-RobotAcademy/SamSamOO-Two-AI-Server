"""
대시보드 API 라우터
"""
from fastapi import APIRouter, HTTPException, Depends

from dashboard.application.usecase.dashboard_usecase import DashboardUseCase
from dashboard.infrastructure.repository.statistics_repository_impl import StatisticsRepositoryImpl
from dashboard.adapter.input.web.response.dashboard_response import (
    DashboardStatisticsResponse,
    PlatformDistributionResponse,
    CategoryDistributionResponse,
    PlatformDistributionItem,
    CategoryDistributionItem
)
from config.helpers.utils.redis_utils import get_current_user_id


# 리포지토리 및 유스케이스 초기화 (product_router와 동일한 패턴)
_statistics_repo = StatisticsRepositoryImpl()
dashboard_uc = DashboardUseCase(_statistics_repo)

dashboard_router = APIRouter(tags=["dashboard"])


@dashboard_router.get("/statistics", response_model=DashboardStatisticsResponse)
def get_dashboard_statistics(seller_id: int = Depends(get_current_user_id)):
    """
    대시보드 전체 통계를 조회합니다. (Full Path: /dashboard/statistics)
    로그인한 사용자의 상품만 조회합니다.
    """
    try:
        statistics = dashboard_uc.get_dashboard_statistics(seller_id)

        # Dict[str, dict] -> Dict[str, Item] 변환 (빈 dict도 처리)
        platform_dist = {
            platform: PlatformDistributionItem(**data)
            for platform, data in statistics.platform_distribution.items()
        } if statistics.platform_distribution else {}

        category_dist = {
            category: CategoryDistributionItem(**data)
            for category, data in statistics.category_distribution.items()
        } if statistics.category_distribution else {}

        return DashboardStatisticsResponse(
            platform_distribution=platform_dist,
            category_distribution=category_dist,
            total_products=statistics.total_products
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")


@dashboard_router.get("/platform-distribution", response_model=PlatformDistributionResponse)
def get_platform_distribution(seller_id: int = Depends(get_current_user_id)):
    """
    플랫폼별 상품 분포만 조회합니다. (Full Path: /dashboard/platform-distribution)
    로그인한 사용자의 상품만 조회합니다.
    """
    try:
        distribution = dashboard_uc.get_platform_distribution(seller_id)

        # dict -> PlatformDistributionResponse 변환 (빈 dict도 처리)
        response_data = {
            platform: PlatformDistributionItem(**data)
            for platform, data in distribution.items()
        } if distribution else {}

        return PlatformDistributionResponse(**response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"플랫폼별 분포 조회 실패: {str(e)}")


@dashboard_router.get("/category-distribution", response_model=CategoryDistributionResponse)
def get_category_distribution(seller_id: int = Depends(get_current_user_id)):
    """
    카테고리별 상품 분포만 조회합니다. (Full Path: /dashboard/category-distribution)
    로그인한 사용자의 상품만 조회합니다.
    """
    try:
        distribution = dashboard_uc.get_category_distribution(seller_id)

        # dict -> CategoryDistributionResponse 변환 (빈 dict도 처리)
        response_data = {
            category: CategoryDistributionItem(**data)
            for category, data in distribution.items()
        } if distribution else {}

        return CategoryDistributionResponse(**response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"카테고리별 분포 조회 실패: {str(e)}")