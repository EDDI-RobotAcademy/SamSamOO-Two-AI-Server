from typing import List, Optional
import uuid
import json

from sqlalchemy.exc import NoResultFound
from sqlalchemy import text

from config.database.session import get_db_session
from sqlalchemy.orm import Session

from product_analysis.infrastructure.orm.analysis_job_orm import AnalysisJobORM
from product_analysis.infrastructure.orm.analysis_result_orm import AnalysisResultORM
from product_analysis.infrastructure.orm.insight_result_orm import InsightResultORM
from review.infrastructure.orm.review_orm import ReviewORM
from product_analysis.application.port.analysis_repository_port import (
    AnalysisRepositoryPort, ReviewData, AnalysisMetricsData, AnalysisSummaryData
)


class ReviewAnalysisRepositoryImpl(AnalysisRepositoryPort):
    def __init__(self):
        self.db: Session = get_db_session()

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

    # ⭐️ ------------------ 5. 추가: 최신 분석 결과 조회 ------------------
    def get_latest_analysis_by_product(self, source: str, product_id: str) -> Optional[dict]:
        """상품별 최신 분석 결과 조회"""
        try:
            print(f"[REPO] 최신 분석 결과 조회: {source} / {product_id}")

            query = text("""
                SELECT ar.* 
                FROM analysis_result ar
                INNER JOIN analysis_jobs aj ON ar.job_id = aj.id
                WHERE aj.source = :source AND aj.source_product_id = :product_id
                ORDER BY ar.created_at DESC
                LIMIT 1
            """)

            row = self.db.execute(
                query,
                {"source": source, "product_id": product_id}
            ).fetchone()

            if not row:
                print(f"[REPO] 분석 결과 없음")
                return None

            print(f"[REPO] 분석 결과 발견: job_id={row.job_id}")

            return {
                "job_id": row.job_id,
                "total_reviews": row.total_reviews,
                "sentiment_json": json.loads(row.sentiment_json) if row.sentiment_json else None,
                "aspects_json": json.loads(row.aspects_json) if row.aspects_json else None,
                "keywords_json": json.loads(row.keywords_json) if row.keywords_json else [],
                "issues_json": json.loads(row.issues_json) if row.issues_json else [],
                "trend_json": json.loads(row.trend_json) if row.trend_json else None,
                "created_at": row.created_at.isoformat() if row.created_at else None
            }

        except Exception as e:
            print(f"[REPO ERROR] 최신 분석 결과 조회 실패: {e}")
            self.db.rollback()
            return None

    def get_latest_insight_by_job_id(self, job_id: str) -> Optional[dict]:
        """job_id로 최신 인사이트 조회"""
        try:
            print(f"[REPO] 인사이트 조회: job_id={job_id}")

            query = text("""
                SELECT * FROM insight_result 
                WHERE job_id = :job_id
                ORDER BY created_at DESC
                LIMIT 1
            """)

            row = self.db.execute(query, {"job_id": job_id}).fetchone()

            if not row:
                print(f"[REPO] 인사이트 없음")
                return None

            print(f"[REPO] 인사이트 발견")

            return {
                "job_id": row.job_id,
                "summary": row.summary,
                "insights_json": json.loads(row.insights_json) if row.insights_json else {},
                "metadata_json": json.loads(row.metadata_json) if row.metadata_json else {},
                "evidence_ids": json.loads(row.evidence_ids) if row.evidence_ids else [],
                "created_at": row.created_at.isoformat() if row.created_at else None
            }

        except Exception as e:
            print(f"[REPO ERROR] 인사이트 조회 실패: {e}")
            self.db.rollback()
            return None