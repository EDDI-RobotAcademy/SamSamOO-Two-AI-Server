from typing import Dict, Any

from sqlalchemy import (
    Column, String, Integer, DateTime, BigInteger, ForeignKey, JSON
)
from datetime import datetime
from config.database.session import Base

class AnalysisResultORM(Base):
    """
    Analyzer 결과 및 상세 지표(Metrics) 테이블.
    """
    __tablename__ = 'analysis_result'

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # 결과 PK
    job_id = Column(String(255), ForeignKey('analysis_jobs.id'), unique=True, nullable=False)  # Job 참조

    total_reviews = Column(Integer, default=0)

    # JSON Fields
    sentiment_json = Column(JSON, nullable=True)
    aspects_json = Column(JSON, nullable=True)
    keywords_json = Column(JSON, nullable=True)
    issues_json = Column(JSON, nullable=True)
    trend_json = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_metrics_data(self) -> Dict[str, Any]:
        """도메인 엔티티 변환용 데이터 딕셔너리."""
        return {
            "total_reviews": self.total_reviews,
            "sentiment_json": self.sentiment_json,
            "aspects_json": self.aspects_json,
            "keywords_json": self.keywords_json,
            "issues_json": self.issues_json,
            "trend_json": self.trend_json
        }