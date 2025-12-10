# review/infrastructure/repository/crawling_status_repository_impl.py
from typing import Optional
from sqlalchemy.orm import Session

from review.infrastructure.repository.crawling_status_repository import CrawlingStatusRepository
from review.domain.entity.crawling_status import CrawlingStatus
from review.infrastructure.orm.crawling_status_orm import CrawlingStatusORM
from config.database.session import get_db_session


class CrawlingStatusRepositoryImpl(CrawlingStatusRepository):
    """크롤링 상태 저장소 구현체"""

    def __init__(self, session: Session = None):
        self.session = session or get_db_session()

    def save(self, status: CrawlingStatus) -> None:
        """상태 저장 (Upsert)"""
        existing = self.session.query(CrawlingStatusORM).filter_by(
            product_id=status.product_id
        ).first()

        if existing:
            # 업데이트
            existing.status = status.status.value
            existing.progress = status.progress
            existing.started_at = status.started_at
            existing.completed_at = status.completed_at
            existing.error_message = status.error_message
            existing.total_reviews = status.total_reviews
        else:
            # 새로 생성
            orm = CrawlingStatusORM.from_entity(status)
            self.session.add(orm)

        self.session.commit()

    def find_by_product_id(self, product_id: str) -> Optional[CrawlingStatus]:
        """상품 ID로 상태 조회"""
        orm = self.session.query(CrawlingStatusORM).filter_by(
            product_id=product_id
        ).first()

        return orm.to_entity() if orm else None

    def find_latest_by_product_id(self, product_id: str) -> Optional[CrawlingStatus]:
        """가장 최근 상태 조회"""
        orm = self.session.query(CrawlingStatusORM).filter_by(
            product_id=product_id
        ).order_by(CrawlingStatusORM.created_at.desc()).first()

        return orm.to_entity() if orm else None