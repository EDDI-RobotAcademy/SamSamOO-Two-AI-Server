from typing import List
from abc import ABC, abstractmethod

from review.adapter.input.web.response.review_display_response import ReviewDisplayResponse


class ReviewViewRepositoryPort(ABC):
    @abstractmethod
    def get_reviews_for_display(self, source : str,product_id: str,limit: int = 100) -> List[ReviewDisplayResponse]:
        pass