from typing import List
from samsam_naver.infrastructure.naver_crawler import NaverCrawler
from samsam_naver.domain.product import Product
from samsam_naver.domain.review import Review

class NaverService:

    @staticmethod
    def get_products(query: str) -> List[Product]:
        return NaverCrawler.search_products(query)

    @staticmethod
    def get_reviews(product: Product) -> List[Review]:
        return NaverCrawler.get_reviews(product)
