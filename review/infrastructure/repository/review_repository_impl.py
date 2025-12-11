from typing import List

from review.application.port.review_repository_port import ReviewRepositoryPort
from review.domain.entity.review import Review, ReviewPlatform
from sqlalchemy.orm import Session
from review.infrastructure.orm.review_orm import ReviewORM
from sqlalchemy import select

# review/infrastructure/repository/review_repository_impl.py
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from review.application.port.review_repository_port import ReviewRepositoryPort
from review.domain.entity.review import Review, ReviewPlatform
from review.infrastructure.orm.review_orm import ReviewORM


class ReviewRepositoryImpl(ReviewRepositoryPort):
    def __init__(self, session: Session):
        self.db: Session = session

    def save_all(self, reviews: List[Review], source: str, source_product_id: str) -> None:
        """리뷰 일괄 저장 (중복 방지 포함)"""

        if not reviews:
            print("[SAVE] 저장할 리뷰가 없습니다.")
            return

        print(f"\n{'=' * 60}")
        print(f"[SAVE] 리뷰 저장 시작")
        print(f"  대상: {source}/{source_product_id}")
        print(f"  수집: {len(reviews)}개")

        # ===== 1. 저장 전 기존 개수 =====
        before_count = self.db.query(func.count(ReviewORM.review_id)).filter(
            ReviewORM.source == source,
            ReviewORM.source_product_id == source_product_id
        ).scalar()
        print(f"  DB 기존: {before_count}개")

        # ===== 2. 기존 리뷰 조회 (중복 체크) =====
        existing = self.db.query(
            ReviewORM.reviewer,
            ReviewORM.content,
            ReviewORM.review_at
        ).filter(
            ReviewORM.source == source,
            ReviewORM.source_product_id == source_product_id
        ).all()

        existing_set = {
            (row.reviewer, row.content, row.review_at)
            for row in existing
        }

        # ===== 3. 신규 리뷰만 필터링 =====
        new_reviews = []
        dup_count = 0

        for r in reviews:
            key = (r.reviewer, r.content, r.review_at)
            if key not in existing_set:
                new_reviews.append(r)
                existing_set.add(key)  # 현재 배치 내 중복도 방지
            else:
                dup_count += 1

        print(f"  중복: {dup_count}개")
        print(f"  신규: {len(new_reviews)}개")

        if not new_reviews:
            print("[SAVE] 모두 중복, 저장 생략")
            print(f"{'=' * 60}\n")
            return

        # ===== 4. 저장 =====
        orm_rows = []
        for r in new_reviews:
            row = ReviewORM(
                source=source,
                source_product_id=source_product_id,
                reviewer=r.reviewer,
                rating=r.rating,
                content=r.content,
                review_at=r.review_at,
                collected_at=r.collected_at
            )
            orm_rows.append(row)

        self.db.bulk_save_objects(orm_rows)
        self.db.flush()

        # ===== 5. 저장 후 확인 =====
        after_count = self.db.query(func.count(ReviewORM.review_id)).filter(
            ReviewORM.source == source,
            ReviewORM.source_product_id == source_product_id
        ).scalar()

        actual_increase = after_count - before_count
        print(f"  DB 저장 후: {after_count}개")
        print(f"  실제 증가: {actual_increase}개")

        if actual_increase != len(new_reviews):
            print(f"  ⚠️ 불일치! 예상: {len(new_reviews)}, 실제: {actual_increase}")

        print(f"[SAVE] 완료")
        print(f"{'=' * 60}\n")

    def save(self, review: Review, source: str, source_product_id: str) -> None:
        """단일 리뷰 저장"""
        self.save_all([review], source, source_product_id)

    def find_by_product_id(self, product_id: str, platform: str) -> List[Review]:
        query = select(ReviewORM).where(
            ReviewORM.source_product_id == product_id,
            ReviewORM.source == platform
        )
        orm_reviews = self.db.execute(query).scalars().all()

        domain_reviews = []
        for r_orm in orm_reviews:
            try:
                platform_enum = ReviewPlatform.from_string(r_orm.source)
            except ValueError:
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