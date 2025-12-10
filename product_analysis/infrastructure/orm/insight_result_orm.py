from typing import Dict, Any

from sqlalchemy import (
    Column, String, DateTime, Text, BigInteger, ForeignKey, JSON,
)
from datetime import datetime
from config.database.session import Base

class InsightResultORM(Base):
    """
    LLM 요약 및 인사이트 테이블.
    """
    __tablename__ = 'insight_result'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_id = Column(String(255), ForeignKey('analysis_jobs.id'), unique=True, nullable=False)  # Job 참조

    summary = Column(Text, nullable=False)

    insights_json = Column(JSON, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    evidence_ids = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_summary_data(self) -> Dict[str, Any]:
        """도메인 엔티티 변환용 데이터 딕셔너리."""
        return {
            "summary": self.summary,
            "insights_json": self.insights_json,
            "metadata_json": self.metadata_json,
            "evidence_ids": self.evidence_ids
        }