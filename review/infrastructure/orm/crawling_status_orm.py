# review/infrastructure/orm/crawling_status_orm.py
from sqlalchemy import Column, String, Integer, DateTime, Text
from datetime import datetime

# ⭐️ 이렇게 수정!
from config.database.session import Base


class CrawlingStatusORM(Base):
    __tablename__ = "crawling_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(100), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    progress = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    total_reviews = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_entity(self):
        """ORM -> Entity 변환"""
        from review.domain.entity.crawling_status import CrawlingStatus, CrawlingStatusEnum
        return CrawlingStatus(
            product_id=self.product_id,
            status=CrawlingStatusEnum(self.status),
            progress=self.progress,
            started_at=self.started_at,
            completed_at=self.completed_at,
            error_message=self.error_message,
            total_reviews=self.total_reviews
        )

    @staticmethod
    def from_entity(entity):
        """Entity -> ORM 변환"""
        return CrawlingStatusORM(
            product_id=entity.product_id,
            status=entity.status.value,
            progress=entity.progress,
            started_at=entity.started_at,
            completed_at=entity.completed_at,
            error_message=entity.error_message,
            total_reviews=entity.total_reviews
        )