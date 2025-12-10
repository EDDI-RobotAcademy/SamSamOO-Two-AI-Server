from typing import Dict

from product.domain.entity.product import Product
from review.domain.service.review_collection_service import ReviewCollectionService
from review.application.port.scraper_port import ScraperPort
from review.infrastructure.repository.review_repository_impl import ReviewRepositoryImpl
from review.infrastructure.repository.crawling_status_repository import CrawlingStatusRepository


class CollectReviewsUseCase:
    """리뷰 수집 유스케이스"""

    def __init__(
        self,
        scraper: ScraperPort,
        review_repository: ReviewRepositoryImpl,
        status_repository: CrawlingStatusRepository
    ):
        self.collection_service = ReviewCollectionService(
            scraper=scraper,
            review_repository=review_repository,
            status_repository=status_repository
        )

    def execute(self, product: Product) -> Dict:
        """리뷰 수집 실행"""
        return self.collection_service.collect_and_save_reviews(product)


class GetCollectionStatusUseCase:
    """수집 상태 조회 유스케이스"""

    def __init__(self, status_repository: CrawlingStatusRepository):
        self.status_repository = status_repository

    def execute(self, product_id: str):
        """상태 조회 실행"""
        from review.domain.entity.crawling_status import CrawlingStatus

        status = self.status_repository.find_by_product_id(product_id)
        if status is None:
            # 상태가 없으면 새로 생성 (IDLE)
            status = CrawlingStatus.create_new(product_id)

        return status