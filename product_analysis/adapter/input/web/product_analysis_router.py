from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database.session import get_db_session as get_db
import os
import traceback

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
def run_analysis_for_product(
        source: str,
        source_product_id: str,
        db: Session = Depends(get_db)  # ⭐️ 요청 시 DB Session 주입
):
    # ⭐️ Repository를 함수 내부에서 Session과 함께 생성
    analysis_repo = ReviewAnalysisRepositoryImpl(session=db)

    # LLM 어댑터 생성
    llm = LLMAdapterImpl(api_key=OPENAI_API_KEY)

    # 도메인 서비스 생성
    analysis_service = ReviewAnalysisService(
        llm_port=llm,
        analysis_repo=analysis_repo  # ⭐️ 내부 Repository 사용
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
# 분석 결과 조회 (GET - by job_id)
# =========================================================
@analysis_router.get(
    "/job/{job_id}/results",
    response_model=AnalysisResultsResponse
)
def get_analysis_results(
        job_id: str,
        db: Session = Depends(get_db)  # ⭐️ 요청 시 DB Session 주입
):
    # ⭐️ Repository를 함수 내부에서 Session과 함께 생성
    analysis_repo = ReviewAnalysisRepositoryImpl(session=db)

    metrics_data = analysis_repo.get_analysis_metrics(job_id)  # ⭐️ 내부 Repository 사용
    summary_data = analysis_repo.get_insight_summary(job_id)  # ⭐️ 내부 Repository 사용

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


# =========================================================
# 분석 결과 조회 (GET - 최신 결과)
# =========================================================
@analysis_router.get("/{source}/{product_id}/latest")  # ⭐️ 404를 해결하기 위해 경로 정의를 확인했습니다.
def get_latest_analysis(
        source: str,
        product_id: str,
        db: Session = Depends(get_db)  # ⭐️ 요청 시 DB Session 주입
):
    """최신 분석 결과 조회"""

    # ⭐️ Repository를 함수 내부에서 Session과 함께 생성
    analysis_repo = ReviewAnalysisRepositoryImpl(session=db)

    print(f"[INFO] 최신 분석 결과 조회: {source} / {product_id}")

    try:
        # Repository를 통해 최신 분석 결과 조회
        analysis_result = analysis_repo.get_latest_analysis_by_product(
            source=source,
            product_id=product_id
        )

        if not analysis_result:
            print(f"[INFO] 분석 결과 없음: {source} / {product_id}")
            raise HTTPException(status_code=404, detail="분석 결과가 없습니다")

        job_id = analysis_result.get("job_id")
        print(f"[INFO] 분석 결과 발견: job_id={job_id}")

        # Repository를 통해 인사이트 조회
        insight_result = analysis_repo.get_latest_insight_by_job_id(job_id)

        print(f"[SUCCESS] 분석 결과 반환 완료")

        return {
            "analysis_result": analysis_result,
            "insight_result": insight_result
        }

    except HTTPException:
        # 404 등의 HTTP 예외는 재발생시킵니다.
        raise
    except Exception as e:
        print(f"[ERROR] 분석 결과 조회 실패: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))