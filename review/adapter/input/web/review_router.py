from fastapi import APIRouter, status, Query, HTTPException
from app.tasks.tasks import start_review_crawl_task ,start_review_analysis_task
from review.adapter.input.web.request.review_reanalyze_request import ReviewReanalyzeRequest
from review.adapter.input.web.response.task_start_response import TaskStartResponse
from review.adapter.input.web.request.crawl_review_request import FetchReviewsRequest
from review.infrastructure.repository.review_view_repository_impl import ReviewViewRepositoryImpl
from review.adapter.input.web.request.review_analyze_request import ReviewAnalyzeRequest
from review.infrastructure.repository.product_repository_impl import ProductRepositoryImpl
from review.infrastructure.repository.analysis_job_repository_impl import AnalysisJobRepositoryImpl
from review.infrastructure.repository.analysis_result_repository_impl import AnalysisResultRepositoryImpl
from review.infrastructure.repository.insight_result_repository_impl import InsightResultRepositoryImpl
from review.application.usecase.recollect_reviews_usecase import RecollectReviewsUseCase
from review.application.usecase.delete_review_usecase import DeleteReviewsUseCase
from product.domain.entity.product import AnalysisStatus
from review.infrastructure.repository.review_repository_impl import ReviewRepositoryImpl
from celery import chain
from config.database.session import get_db_session

review_router = APIRouter(tags=["review"])
review_view_repo = ReviewViewRepositoryImpl()
product_repo     = ProductRepositoryImpl()
review_repo      = ReviewRepositoryImpl()
job_repo         = AnalysisJobRepositoryImpl()
analysis_repo    = AnalysisResultRepositoryImpl()
insight_repo     = InsightResultRepositoryImpl()
deleter   = DeleteReviewsUseCase(analysis_repo, insight_repo, job_repo, review_repo)
recollect = RecollectReviewsUseCase(deleter, product_repo, crawler_queue=None)  # ← 큐 없이

@review_router.post(
    "/collect/start",
    response_model=TaskStartResponse,
    status_code=status.HTTP_202_ACCEPTED
)
def fetch_reviews(
    req: FetchReviewsRequest,
):
    platform = req.platform
    product_id = str(req.product_id)

    # ⭐️⭐️⭐️ 1. Celery Task를 호출하고 즉시 응답 ⭐️⭐️⭐️
    task = start_review_crawl_task.delay(
        platform=platform,
        source_product_id=product_id
    )

    # 2. 비동기 작업 수락 응답 반환
    return TaskStartResponse(
        task_id=task.id,
        platform=platform,
        product_id=product_id,
        message="Review crawling task successfully started.",
        # ⭐️ 프론트엔드가 폴링해야 할 URL ⭐️
        polling_url=f"/review/collect/status/{platform}/{product_id}"
    )


@review_router.post(
    "/reanalyze/start",
    response_model=TaskStartResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def start_reanalyze(req: ReviewReanalyzeRequest):
    """
    리뷰 '재분석' Celery 태스크 수동 실행 엔드포인트
    - 기존 수집 데이터(reviews)는 그대로 두고, 분석만 다시 수행
    - 실제 상태 전이(ANALYZING/ANALYZED)와 이전 분석 결과 정리(clear_previous)는 태스크 내부에서 처리
    """
    platform = req.platform
    product_id = str(req.product_id)

    # Celery 태스크 호출 (기존 analysis.start 재사용)
    task = start_review_crawl_task.apply_async(kwargs={
        "previous_result": {
            "platform": platform,
            "source_product_id": product_id,
            # 태스크에서 필요하면 옵션 사용
            "options": {"clear_previous": req.clear_previous}
        }
    })

    return TaskStartResponse(
        task_id=task.id,
        platform=platform,
        product_id=product_id,
        message="Review re-analysis task successfully started.",
        polling_url=f"/review/analyze/status/{platform}/{product_id}",
    )

# 수동 트리거 -> 분석 실패시 -> 테스트 필요
@review_router.post(
    "/analyze/start",
    response_model=TaskStartResponse,
    status_code=status.HTTP_202_ACCEPTED
)
def start_analyze(req: ReviewAnalyzeRequest):
    """
    리뷰 분석 Celery 태스크 수동 실행 엔드포인트
    """
    platform = req.platform
    product_id = str(req.product_id)

    task = start_review_analysis_task.apply_async(
        kwargs={"previous_result": {"platform": platform, "source_product_id": product_id}}
    )

    return TaskStartResponse(
        task_id=task.id,
        platform=platform,
        product_id=product_id,
        message="Review analysis task successfully started.",
        polling_url=f"/review/analyze/status/{platform}/{product_id}"
    )

@review_router.get("/list")
def get_reviews(
    source: str,
    source_product_id: str,
    limit: int = 100
):
    try:
        review_displays = review_view_repo.get_reviews_for_display(
            source=source,
            product_id=source_product_id,
            limit=limit
        )

        print(f"[INFO] 리뷰 조회 성공: {len(review_displays)}개")

        return [review.to_dict() for review in review_displays]

    except Exception as e:
        print(f"[ERROR] 리뷰 조회 실패: {e}")
        import traceback
        traceback.print_exc()
        return []


@review_router.post("/recollect", response_model=TaskStartResponse)
def recollect_reviews(
        source: str = Query(..., description="elevenst | lotteon | ..."),
        source_product_id: str = Query(..., description="플랫폼 상품ID")
):
    """
    재수집: 기존 데이터 삭제 + 재수집 + 재분석
    """
    # ===== 1. 상태 검증 =====
    prod = product_repo.get(source, source_product_id)
    if not prod:
        raise HTTPException(404, "상품이 없습니다.")

    current_status = AnalysisStatus.from_string(prod["analysis_status"])
    if current_status not in [AnalysisStatus.ANALYZED, AnalysisStatus.FAILED]:
        raise HTTPException(
            409,
            f"재수집은 ANALYZED 또는 FAILED 상태에서만 가능합니다. 현재: {current_status.value}"
        )

    # ===== 2. 기존 데이터 삭제 =====
    session = get_db_session()

    try:
        # DeleteReviewsUseCase 실행
        counts = deleter.execute(source, source_product_id)
        print(f"[RECOLLECT] 삭제 완료: {counts}")

        # ===== 3. 상태 초기화: PENDING =====
        product_repo.update_status(
            source=source,
            product_id=source_product_id,
            status=AnalysisStatus.PENDING.value,
            review_count=0
        )

        print(f"[RECOLLECT] 상태 초기화: ANALYZED → PENDING")

        # ===== 4. Task Chain 시작 (크롤링 → 분석) =====
        task_chain = chain(
            start_review_crawl_task.s(
                platform=source,
                source_product_id=source_product_id
            ),
            start_review_analysis_task.s()
        )
        result = task_chain.apply_async()

        print(f"[RECOLLECT] Task Chain 시작: {result.id}")

        return TaskStartResponse(
            task_id=result.id,
            platform=source,
            product_id=source_product_id,
            message="재수집이 시작되었습니다. 기존 데이터가 삭제되고 새로 수집합니다.",
            polling_url=f"/review/collect/status/{source}/{source_product_id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 재수집 시작 실패: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"재수집 시작 실패: {str(e)}")
    finally:
        session.close()