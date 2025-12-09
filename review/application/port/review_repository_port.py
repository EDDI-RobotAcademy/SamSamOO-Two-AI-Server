from abc import ABC, abstractmethod
from typing import List
from review.domain.entity.review import Review

class ReviewRepositoryPort(ABC):
    @abstractmethod
    def save_all(self, reviews: List[Review]) -> None: ...
    @abstractmethod
    def find_by_product_id(self, product_id: str, platform: str) -> List[Review]: ...