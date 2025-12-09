from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class AnalysisMetrics(BaseModel):
    total_reviews: int
    sentiment: Dict[str, Any] = Field(..., alias="sentiment_json", description="감성 비율 (긍/부/중립)")
    aspects: Dict[str, Any] = Field(..., alias="aspects_json", description="속성별 감성 결과")
    keywords: List[str] = Field(..., alias="keywords_json", description="주요 키워드 목록")
    issues: List[str] = Field(..., alias="issues_json", description="급증 이슈 키워드 목록")
    trend: Dict[str, Any] = Field(..., alias="trend_json", description="주차별 감성 변화 추이")


class InsightSummary(BaseModel):
    summary: str = Field(..., description="LLM이 생성한 전체 요약 텍스트")
    insights: Dict[str, Any] = Field(..., alias="insights_json", description="마케팅/품질 인사이트 구조")
    metadata: Dict[str, Any] = Field(..., alias="metadata_json", description="분석 기간/버전 등 메타데이터")


class AnalysisResultsResponse(BaseModel):
    job_id: str
    metrics: Optional[AnalysisMetrics] = Field(None, description="Analyzer (analysis_result) 결과")
    summary: Optional[InsightSummary] = Field(None, description="LLM 요약 (insight_result) 결과")


class AnalysisRunResponse(BaseModel):
    status: str = Field(..., description="Job 실행 상태 (success, failed, NO_REVIEWS)")
    message: str = Field(..., description="응답 메시지")
    job_id: Optional[str] = Field(None, description="생성된 분석 Job ID")
    data: Optional[Dict[str, Any]] = Field(None, description="추가 데이터 (예: FAILED 시 에러 정보)")