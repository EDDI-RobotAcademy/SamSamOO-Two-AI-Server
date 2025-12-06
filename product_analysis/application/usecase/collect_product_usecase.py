from typing import List
from product_analysis.application.port.product_repository_port import ProductRepositoryPort
from product_analysis.application.port.review_repository_port import ReviewRepositoryPort
from product_analysis.application.port.scraper_port import ScraperPort
from product_analysis.domain.entity.product import Product
from product_analysis.domain.entity.review import Review

class CollectProductUseCase:
    def __init__(self, scraper: ScraperPort, product_repo: ProductRepositoryPort, review_repo: ReviewRepositoryPort):
        self.scraper = scraper
        self.product_repo = product_repo
        self.review_repo = review_repo

    def execute(self, keyword: str, limit_products: int, limit_reviews: int) -> List[Product]:
        products: List[Product] = self.scraper.search_products(keyword, limit_products)
        saved: List[Product] = []
        for p in products:
            # 중복 체크
            exist = self.product_repo.find_by_item_code(p.source, p.item_code)
            if exist:
                prod = exist
            else:
                prod = self.product_repo.save(p)
            # 리뷰 수집
            reviews: List[Review] = self.scraper.fetch_reviews(prod, limit_reviews)
            for r in reviews:
                r.product_id = prod.id
            self.review_repo.save_all(reviews)
            saved.append(prod)
        return saved
