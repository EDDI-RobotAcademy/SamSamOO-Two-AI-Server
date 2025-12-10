# product_analysis/application/port/llm_analysis_port.py

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


# 🚨 LLM 분석 실패를 알리는 커스텀 예외 추가
class LLMAnalysisFailure(Exception):
    """LLM API 호출 또는 결과 파싱 실패 시 발생하는 예외."""
    pass


ReviewData = Dict[str, Any]
AnalysisMetricsData = Dict[str, Any]
AnalysisSummaryData = Dict[str, Any]


class AnalysisRepositoryPort(ABC):
    # 1. 리뷰 데이터 조회
    @abstractmethod
    def get_reviews_by_product_source_id(self, source: str, source_product_id: str, limit: int = 100) -> List[
        ReviewData]:
        """특정 상품에 해당하는 리뷰 데이터를 DB에서 조회합니다."""
        raise NotImplementedError

    # 2. Job 관리
    @abstractmethod
    def create_analysis_job(self, source: str, source_product_id: str) -> str:
        """분석 Job 레코드를 생성하고 Job ID를 반환합니다."""
        raise NotImplementedError

    @abstractmethod
    def update_job_status(self, job_id: str, status: str):
        """Job 상태를 업데이트합니다. (예: RUNNING, FAILED, COMPLETED)"""
        raise NotImplementedError

    # 3. Metrics 저장 및 조회 (AnalysisResultORM)
    @abstractmethod
    def save_analysis_metrics(self, job_id: str, metrics: AnalysisMetricsData):
        """Job ID에 해당하는 상세 지표(Metrics)를 저장합니다."""
        raise NotImplementedError

    @abstractmethod
    def get_analysis_metrics(self, job_id: str) -> Optional[AnalysisMetricsData]:
        """Job ID로 상세 지표(Metrics)를 조회합니다."""
        raise NotImplementedError

    # 4. Summary 저장 및 조회 (InsightResultORM)
    @abstractmethod
    def save_insight_summary(self, job_id: str, summary_data: AnalysisSummaryData):
        """Job ID에 해당하는 최종 요약 및 인사이트를 저장합니다."""
        raise NotImplementedError

    @abstractmethod
    def get_insight_summary(self, job_id: str) -> Optional[AnalysisSummaryData]:
        """Job ID로 최종 요약(Summary) 결과를 조회합니다."""
        raise NotImplementedError


class LLMAnalysisPort(ABC):
    # (LLMAnalysisPort의 정의가 누락되어 있지만, 이 클래스에 LLM 관련 예외를 포함하는 것이 좋습니다.)
    @abstractmethod
    def extract_job_metrics(self, review_texts: List[str], product_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate_final_summary(self, review_texts: List[str], metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError