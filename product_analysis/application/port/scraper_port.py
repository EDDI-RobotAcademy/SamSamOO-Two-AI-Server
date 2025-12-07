from abc import ABC, abstractmethod
from typing import List
from product.domain.entity.product import Product
from product_analysis.domain.entity.review import Review

class ScraperPort(ABC):
    @abstractmethod
    def search_products(self, keyword: str, limit: int) -> List[Product]: ...
    @abstractmethod
    def fetch_reviews(self, product: Product, limit: int) -> List[Review]: ...
