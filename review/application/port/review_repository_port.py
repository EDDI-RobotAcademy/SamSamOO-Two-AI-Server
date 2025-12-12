from abc import ABC, abstractmethod
from typing import List
from review.domain.entity.review import Review

class ReviewRepositoryPort(ABC):
    @abstractmethod
    def save_all(self, reviews: List[Review], source: str, source_product_id: str) -> None: ...
    @abstractmethod
    def find_by_product_id(self, product_id: str, platform: str) -> List[Review]: ...

    @abstractmethod
    def delete_by_product(self, source: str, product_id: str) -> int:
        """해당 상품의 리뷰 삭제, 삭제건수 반환"""
        ...