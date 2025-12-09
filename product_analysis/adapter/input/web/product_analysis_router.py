from fastapi import APIRouter, HTTPException
import os

from product_analysis.adapter.input.web.response.analysis_response import (
    AnalysisRunResponse,
    AnalysisResultsResponse
)
from product_analysis.infrastructure.external.llm_adapter_impl import LLMAdapterImpl
from product_analysis.infrastructure.repository.analysis_repository_impl import ReviewAnalysisRepositoryImpl
from product_analysis.domain.service.analyzer_service import ReviewAnalysisService
from product_analysis.application.usecase.analyze_product_usecase import ProductAnalysisUsecase

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "YOUR_FALLBACK_KEY")

analysis_router = APIRouter(tags=["analysis"])


# =========================================================
# 리뷰 분석 실행 (POST)
# =========================================================
@analysis_router.post(
    "/{source}/{source_product_id}/run",
    response_model=AnalysisRunResponse
)
def run_analysis_for_product(source: str, source_product_id: str):

    # 필요한 인프라스트럭처 인스턴스 생성
    repo = ReviewAnalysisRepositoryImpl()
    llm = LLMAdapterImpl(api_key=OPENAI_API_KEY)

    # 도메인 서비스 생성
    analysis_service = ReviewAnalysisService(
        llm_port=llm,
        analysis_repo=repo
    )

    # Usecase 생성
    analysis_uc = ProductAnalysisUsecase(analysis_service)

    # 실행
    result = analysis_uc.execute(source=source, source_product_id=source_product_id)

    job_id = result.get("job_id")
    status = result.get("status")

    if status == "NO_REVIEWS":
        return AnalysisRunResponse(
            status="success",
            message="No reviews found.",
            job_id=None
        )

    if status == "FAILED":
        raise HTTPException(
            status_code=500,
            detail=f"Analysis Job {job_id} failed."
        )

    return AnalysisRunResponse(
        status="success",
        message=f"Analysis Job {job_id} completed.",
        job_id=job_id,
        data=result.get("result_data")
    )


# =========================================================
# 분석 결과 조회 (GET)
# =========================================================
@analysis_router.get(
    "/job/{job_id}/results",
    response_model=AnalysisResultsResponse
)
def get_analysis_results(job_id: str):

    # 인프라스트럭처 → Repository만 필요
    repo = ReviewAnalysisRepositoryImpl()

    metrics_data = repo.get_analysis_metrics(job_id)
    summary_data = repo.get_insight_summary(job_id)

    if not metrics_data and not summary_data:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis results for Job ID {job_id} not found."
        )

    return AnalysisResultsResponse(
        job_id=job_id,
        metrics=metrics_data,
        summary=summary_data
    )
