from typing import List

from product.domain.entity.product import Product, Platform
from review.application.port.scraper_port import ScraperPort
from review.application.port.review_repository_port import ReviewRepositoryPort
from review.domain.entity.review import Review


class FetchReviewsUseCase:

    def __init__(self, scraper: ScraperPort, repository: ReviewRepositoryPort):
        self.scraper = scraper
        self.repository = repository

    def execute(self, product: Product) -> List[Review]:

        reviews = self.scraper.fetch_reviews(product)

        if isinstance(product.source, Platform):
            source_value = product.source.value
        else:
            source_value = str(product.source)

        self.repository.save_all(
            reviews,
            source=source_value,
            source_product_id=product.source_product_id
        )
        return reviews