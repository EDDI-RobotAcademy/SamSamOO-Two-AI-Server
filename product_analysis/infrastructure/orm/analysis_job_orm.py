from sqlalchemy import (
    Column, String, DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database.session import Base

class AnalysisJobORM(Base):
    """
    분석 Job의 상태를 관리하는 부모 테이블. (analysis_jobs)
    """
    __tablename__ = 'analysis_jobs'

    id = Column(String(255), primary_key=True)  # PK: job_id (UUID 문자열)

    # 분석 대상 상품 식별자
    source = Column(String(50), nullable=False)
    source_product_id = Column(String(255), nullable=False)

    status = Column(String(50), default="PENDING")

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship 정의: AnalysisResultORM와 InsightResultORM에서 이 Job을 참조합니다.
    metrics_result = relationship("AnalysisResultORM", backref="job", uselist=False)
    insight_result = relationship("InsightResultORM", backref="job", uselist=False)