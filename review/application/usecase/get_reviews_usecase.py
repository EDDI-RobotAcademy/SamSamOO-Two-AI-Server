from typing import List

from review.application.port.review_view_repository_port import ReviewViewRepositoryPort
from review.adapter.input.web.response.review_display_response import ReviewDisplayResponse


class GetReviewsUseCase:

    def __init__(self, review_view_repo: ReviewViewRepositoryPort):
        self.review_view_repo = review_view_repo

    def execute(
        self,
        source: str,
        product_id: str,
        limit: int = 100
    ) -> List[ReviewDisplayResponse]:
        reviews = self.review_view_repo.get_reviews_for_display(
            source=source,
            product_id=product_id,
            limit=limit
        )

        return reviews