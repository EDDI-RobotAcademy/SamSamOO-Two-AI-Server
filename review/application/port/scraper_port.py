from abc import ABC, abstractmethod
from typing import List

from product.domain.entity.product import Product
from review.domain.entity.review import Review


class ScraperPort(ABC):
    @abstractmethod
    def fetch_reviews(self, product: Product) -> List[Review]: ...