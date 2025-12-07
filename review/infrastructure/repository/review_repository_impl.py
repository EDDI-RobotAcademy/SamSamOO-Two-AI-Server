from typing import List

from config.database.session import get_db_session
from review.application.port.review_repository_port import ReviewRepositoryPort
from review.domain.entity.review import Review, ReviewPlatform
from sqlalchemy.orm import Session
from review.infrastructure.orm.review_orm import ReviewORM
from sqlalchemy import select

class ReviewRepositoryImpl(ReviewRepositoryPort):
    def __init__(self):
        self.db: Session = get_db_session()

    def save_all(self, reviews: List[Review]) -> None:
        orm_rows = []

        for r in reviews:
            row = ReviewORM(
                source=r.platform.value,
                source_product_id=r.product_id,
                reviewer=r.reviewer,
                rating=r.rating,
                content=r.content,
                review_at=r.review_at,
                collected_at=r.collected_at
            )
            orm_rows.append(row)

        self.db.bulk_save_objects(orm_rows)
        self.db.commit()

    def find_by_product_id(self, product_id: str, platform: str) -> List[Review]:
        """
        특정 상품 ID와 플랫폼에 해당하는 모든 리뷰를 DB에서 조회하여 Review 엔티티로 반환합니다.
        """
        # 1. DB 조회 (SQLAlchemy 2.0 스타일 권장)
        query = select(ReviewORM).where(
            ReviewORM.source_product_id == product_id,
            ReviewORM.source == platform
        )
        orm_reviews = self.db.execute(query).scalars().all()

        # 2. ORM 객체를 Domain Entity (Review)로 변환
        domain_reviews = []
        for r_orm in orm_reviews:

            # Review Entity 생성을 위해 플랫폼 문자열을 Enum으로 변환합니다.
            try:
                platform_enum = ReviewPlatform.from_string(r_orm.source)
            except ValueError:
                # ReviewPlatform에 정의되지 않은 플랫폼이 DB에 있는 경우, 문자열 그대로 유지합니다.
                platform_enum = r_orm.source

            review_entity = Review(
                product_id=r_orm.source_product_id,
                platform=platform_enum,
                reviewer=r_orm.reviewer,
                rating=r_orm.rating,
                content=r_orm.content,
                review_at=r_orm.review_at,
                collected_at=r_orm.collected_at
            )
            domain_reviews.append(review_entity)

        return domain_reviews