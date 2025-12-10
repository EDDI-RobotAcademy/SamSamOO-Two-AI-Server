from typing import Optional
from sqlalchemy.orm import Session

from config.database.session import get_db_session
from review.application.port.crawling_status_port import CrawlingStatusPort
from review.domain.entity.crawling_status import CrawlingStatus
from review.infrastructure.orm.crawling_status_orm import CrawlingStatusORM

class CrawlingStatusRepositoryImpl(CrawlingStatusPort):
    """SQLAlchemy 기반 Port 구현체 (단일 구현)"""

    def __init__(self, session: Session | None = None):
        self.db: Session = session or get_db_session()

    def save(self, status: CrawlingStatus) -> None:
        """product_id 기준 upsert"""
        try:
            existing: Optional[CrawlingStatusORM] = (
                self.db.query(CrawlingStatusORM)
                .filter(CrawlingStatusORM.product_id == status.product_id)
                .first()
            )
            if existing:
                existing.status = getattr(status.status, "value", status.status)
                existing.progress = status.progress
                existing.started_at = status.started_at
                existing.completed_at = status.completed_at
                existing.error_message = status.error_message
                existing.total_reviews = status.total_reviews
            else:
                self.db.add(CrawlingStatusORM.from_entity(status))

            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def find_by_product_id(self, product_id: str) -> Optional[CrawlingStatus]:
        orm = (
            self.db.query(CrawlingStatusORM)
            .filter(CrawlingStatusORM.product_id == product_id)
            .order_by(CrawlingStatusORM.created_at.desc())
            .first()
        )
        return orm.to_entity() if orm else None

    def find_latest_by_product_id(self, product_id: str) -> Optional[CrawlingStatus]:
        # explicit alias
        return self.find_by_product_id(product_id)
