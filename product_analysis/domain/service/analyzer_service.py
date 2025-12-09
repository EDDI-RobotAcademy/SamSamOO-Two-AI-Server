# product_analysis/domain/service/analyzer_service.py

from product_analysis.application.port.llm_analysis_port import LLMAnalysisPort, LLMAnalysisFailure
from product_analysis.application.port.analysis_repository_port import AnalysisRepositoryPort, ReviewData
from product_analysis.domain.entity.analysis_result import JobMetrics
from product_analysis.domain.entity.insight_result import AnalysisSummary
from typing import List, Dict, Any


class ReviewAnalysisService:
    def __init__(self, llm_port: LLMAnalysisPort, analysis_repo: AnalysisRepositoryPort):
        self._llm_port = llm_port
        self._analysis_repo = analysis_repo

    def analyze_product_reviews(self, source: str, source_product_id: str) -> Dict[str, Any]:

        # 1. Job 생성 및 상태 PENDING으로 시작
        job_id = self._analysis_repo.create_analysis_job(source, source_product_id)
        self._analysis_repo.update_job_status(job_id, "RUNNING")

        try:
            # 2. 리뷰 데이터 조회 (Repository Port 사용)
            reviews_data: List[ReviewData] = self._analysis_repo.get_reviews_by_product_source_id(
                source=source,
                source_product_id=source_product_id
            )

            if not reviews_data:
                self._analysis_repo.update_job_status(job_id, "COMPLETED")
                return {"job_id": job_id, "status": "NO_REVIEWS"}

            review_texts = [r['text'] for r in reviews_data]
            total_reviews = len(review_texts)

            # 3. LLM 1단계: Metrics 추출 (LLM Port 사용)
            # LLM 통신 실패 시 LLMAnalysisFailure 발생
            metrics_raw_data = self._llm_port.extract_job_metrics(review_texts, source_product_id)

            # 4. Job Metrics 엔티티로 변환 및 DB 저장 (Repository Port 사용)
            metrics_entity = JobMetrics.from_llm_data(metrics_raw_data, total_reviews)
            self._analysis_repo.save_analysis_metrics(job_id, metrics_entity.to_db_dict())

            # 5. LLM 2단계: 최종 요약 및 인사이트 도출 (LLM Port 사용)
            summary_raw_data = self._llm_port.generate_final_summary(review_texts, metrics_raw_data)

            # 6. Summary 엔티티로 변환 및 DB 저장 (Repository Port 사용)
            summary_entity = AnalysisSummary(
                job_id=job_id,
                summary=summary_raw_data.get('summary', '분석 요약 실패'),
                insights=summary_raw_data.get('insights', {}),
                metadata=summary_raw_data.get('metadata', {}),
                evidence_ids=summary_raw_data.get('evidence_ids', [])
            )
            self._analysis_repo.save_insight_summary(job_id, summary_entity.to_db_dict())

            # 7. Job 상태 COMPLETED로 변경
            self._analysis_repo.update_job_status(job_id, "COMPLETED")
            return {"job_id": job_id, "status": "COMPLETED"}

        except (Exception, LLMAnalysisFailure) as e: # 🚨 LLMAnalysisFailure를 명시적으로 처리
            # 오류 발생 시 Job 상태 FAILED로 변경
            print(f"Analysis Job {job_id} failed: {type(e).__name__} - {e}")
            self._analysis_repo.update_job_status(job_id, "FAILED")
            return {"job_id": job_id, "status": "FAILED"}