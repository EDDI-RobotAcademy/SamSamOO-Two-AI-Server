from typing import List, Optional
import uuid

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from product_analysis.infrastructure.orm.analysis_job_orm import AnalysisJobORM
from product_analysis.infrastructure.orm.analysis_result_orm import AnalysisResultORM
from product_analysis.infrastructure.orm.insight_result_orm import InsightResultORM
from review.infrastructure.orm.review_orm import ReviewORM
from product_analysis.application.port.analysis_repository_port import (
    AnalysisRepositoryPort, ReviewData, AnalysisMetricsData, AnalysisSummaryData
)


class ReviewAnalysisRepositoryImpl(AnalysisRepositoryPort):
    def __init__(self, session: Session):
        self.db: Session = session

    # ------------------ 1. 리뷰 데이터 조회 (ReviewORM 사용) ------------------
    def get_reviews_by_product_source_id(self, source: str, source_product_id: str, limit: int = 100) -> List[
        ReviewData]:
        """
        source 및 source_product_id 복합 키를 사용하여 리뷰 테이블에서 데이터를 조회합니다.
        """
        reviews_data = []
        try:
            # 🚨 ReviewORM을 사용한 실제 DB 조회 로직
            reviews = self.db.query(ReviewORM).filter(
                ReviewORM.source == source,
                ReviewORM.source_product_id == source_product_id
            ).limit(limit).all()

            # ORM 객체를 도메인 친화적인 딕셔너리(ReviewData)로 변환
            reviews_data = [review.to_review_data() for review in reviews]

        except Exception as e:
            # 조회 실패 시 롤백 및 예외 전파
            self.db.rollback()
            raise Exception(f"리뷰 조회 중 DB 오류 발생: {e}")

        return reviews_data

    # ------------------ 2. Job 관리 (AnalysisJobORM 사용) ------------------
    def create_analysis_job(self, source: str, source_product_id: str) -> str:
        job_id = str(uuid.uuid4())
        try:
            new_job = AnalysisJobORM(
                id=job_id,
                source=source,
                source_product_id=source_product_id,
                status="PENDING"
            )
            self.db.add(new_job)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Job 생성 실패: {e}")
        return job_id

    def update_job_status(self, job_id: str, status: str):
        try:
            job = self.db.query(AnalysisJobORM).filter_by(id=job_id).one()
            job.status = status
            self.db.commit()
        except NoResultFound:
            self.db.rollback()
            raise NoResultFound(f"Job ID {job_id}를 찾을 수 없습니다.")
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Job 상태 업데이트 실패: {e}")

    # ------------------ 3. Metrics 저장 및 조회 (AnalysisResultORM 사용) ------------------
    def save_analysis_metrics(self, job_id: str, metrics: AnalysisMetricsData):
        """Metrics 데이터를 저장합니다."""
        try:
            self.db.add(AnalysisResultORM(job_id=job_id, **metrics))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Metrics 저장 실패: {e}")

    def get_analysis_metrics(self, job_id: str) -> Optional[AnalysisMetricsData]:
        """Metrics 데이터를 조회합니다."""
        metrics_orm = self.db.query(AnalysisResultORM).filter_by(job_id=job_id).first()
        return metrics_orm.to_metrics_data() if metrics_orm else None

    # ------------------ 4. Summary 저장 및 조회 (InsightResultORM 사용) ------------------
    def save_insight_summary(self, job_id: str, summary_data: AnalysisSummaryData):
        """Summary 데이터를 저장합니다."""

        orm_data = summary_data.copy()
        orm_data.pop('job_id', None)

        try:
            self.db.add(InsightResultORM(job_id=job_id, **orm_data))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Summary 저장 실패: {e}")

    def get_insight_summary(self, job_id: str) -> Optional[AnalysisSummaryData]:
        """Summary 데이터를 조회합니다."""
        summary_orm = self.db.query(InsightResultORM).filter_by(job_id=job_id).first()
        return summary_orm.to_summary_data() if summary_orm else None