from typing import List
from product_analysis.application.port.review_repository_port import ReviewRepositoryPort
from product_analysis.domain.entity.review import Review

class InMemoryReviewRepository(ReviewRepositoryPort):
    def __init__(self):
        self._data: List[Review] = []
        self._seq = 1

    def save_all(self, reviews: List[Review]) -> None:
        for r in reviews:
            r.id = self._seq
            self._seq += 1
            self._data.append(r)

    def find_by_product_id(self, product_id: int, limit: int = 50) -> List[Review]:
        rows = [r for r in self._data if r.product_id == product_id]
        return rows[:limit]
