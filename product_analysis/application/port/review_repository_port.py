from abc import ABC, abstractmethod
from typing import List
from product_analysis.domain.entity.review import Review

class ReviewRepositoryPort(ABC):
    @abstractmethod
    def save_all(self, reviews: List[Review]) -> None: ...
    @abstractmethod
    def find_by_product_id(self, product_id: int, limit: int = 50) -> List[Review]: ...
