from typing import List
from sqlalchemy import select

from review.infrastructure.orm.review_orm import ReviewORM
from review.adapter.input.web.response.review_display_response import ReviewDisplayResponse
from review.application.port.review_view_repository_port import ReviewViewRepositoryPort
from config.database.session import get_db_session


class ReviewViewRepositoryImpl(ReviewViewRepositoryPort):

    def __init__(self):
        pass

    def get_reviews_for_display(
        self,
        source: str,
        product_id: str,
        limit: int = 100
    ) -> List[ReviewDisplayResponse]:
        db = get_db_session()

        try:
            query = select(ReviewORM).where(
                ReviewORM.source_product_id == product_id,
                ReviewORM.source == source
            ).limit(limit)

            orm_reviews = db.execute(query).scalars().all()

            return [ReviewDisplayResponse.from_orm(orm) for orm in orm_reviews]
        finally:
            db.close()