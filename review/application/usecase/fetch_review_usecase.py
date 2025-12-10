from typing import List

from product.domain.entity.product import Product
from review.application.port.scraper_port import ScraperPort
from review.application.port.review_repository_port import ReviewRepositoryPort
from review.domain.entity.review import Review


class FetchReviewsUseCase:

    def __init__(self, scraper: ScraperPort, repository: ReviewRepositoryPort):
        self.scraper = scraper
        self.repository = repository

    # ⭐️ limit 파라미터 제거
    def execute(self, product: Product) -> List[Review]:

        # ⭐️ limit 없이 모든 리뷰를 요청
        reviews = self.scraper.fetch_reviews(product)

        self.repository.save_all(reviews)
        return reviews