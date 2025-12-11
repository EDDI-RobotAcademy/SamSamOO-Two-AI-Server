from fastapi import APIRouter, status
from app.tasks.tasks import start_review_crawl_task ,start_review_analysis_task
from review.adapter.input.web.response.task_start_response import TaskStartResponse
from review.adapter.input.web.request.crawl_review_request import FetchReviewsRequest
from review.infrastructure.repository.review_view_repository_impl import ReviewViewRepositoryImpl
from review.adapter.input.web.request.review_analyze_request import ReviewAnalyzeRequest


review_router = APIRouter(tags=["review"])
review_view_repo = ReviewViewRepositoryImpl()

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

# 수동 트리거

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