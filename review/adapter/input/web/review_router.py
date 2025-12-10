from fastapi import APIRouter, BackgroundTasks

from product.domain.entity.product import Product
from review.adapter.input.web.request.collect_review_request import CollectReviewsRequest, CollectionStatusResponse
from review.adapter.input.web.response.crawl_review_response import ReviewFetchResponse, ReviewItem  # ReviewItem 추가
from review.application.usecase.collect_reviews_usecase import GetCollectionStatusUseCase, CollectReviewsUseCase
from review.application.usecase.fetch_review_usecase import FetchReviewsUseCase
from review.application.port.scraper_factory import get_scraper_adapter
from review.infrastructure.repository.review_repository_impl import ReviewRepositoryImpl
from review.adapter.input.web.request.crawl_review_request import FetchReviewsRequest
from review.infrastructure.repository.crawling_status_repository_impl import CrawlingStatusRepositoryImpl

_review_repo = ReviewRepositoryImpl()
_status_repo = CrawlingStatusRepositoryImpl()

review_router = APIRouter(tags=["review"])


@review_router.post("/crawl", response_model=ReviewFetchResponse)
def fetch_reviews(req: FetchReviewsRequest):
    # 팩토리 함수를 사용하여 요청(req.platform) 값에 맞는 어댑터를 동적으로 가져옵니다.
    _scraper_adapter = get_scraper_adapter(req.platform)

    review_uc = FetchReviewsUseCase(_scraper_adapter, _review_repo)

    product = Product.create_for_crawl_request(
        platform=req.platform,
        product_id=str(req.product_id)
    )

    reviews = review_uc.execute(product)

    review_items = []
    product_name = "N/A"

    for r in reviews:
        review_items.append(ReviewItem(
            reviewer=r.reviewer,
            rating=r.rating,
            content=r.content,
            review_at=r.review_at
        ))

    return ReviewFetchResponse(
        product_name=product_name,
        platform=req.platform,
        product_id=req.product_id,
        review_count=len(reviews),
        reviews=review_items
    )


@review_router.post("/collect/start")
def start_collection(req: CollectReviewsRequest, background_tasks: BackgroundTasks):
    """리뷰 수집 시작"""

    # 1. 현재 상태 확인
    status_usecase = GetCollectionStatusUseCase(_status_repo)
    current_status = status_usecase.execute(req.product_id)

    if not current_status.can_start_collecting():
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail=f"현재 상태({current_status.status.value})에서는 수집을 시작할 수 없습니다"
        )

    # 2. Product 엔티티 생성
    product = Product.create_for_crawl_request(
        platform=req.platform,
        product_id=req.product_id
    )

    # 3. Scraper 어댑터 가져오기 (팩토리 패턴)
    scraper_adapter = get_scraper_adapter(req.platform)

    # 4. UseCase 생성 및 백그라운드 실행
    collect_usecase = CollectReviewsUseCase(
        scraper=scraper_adapter,
        review_repository=_review_repo,
        status_repository=_status_repo
    )

    # 백그라운드 작업으로 등록
    background_tasks.add_task(collect_usecase.execute, product)

    return {
        "message": "리뷰 수집이 시작되었습니다",
        "product_id": req.product_id,
        "platform": req.platform.value
    }


@review_router.get("/collect/status/{product_id}", response_model=CollectionStatusResponse)
def get_collection_status(product_id: str):
    """수집 상태 조회"""

    print(f"[INFO] 상태 조회 요청: {product_id}")

    try:
        usecase = GetCollectionStatusUseCase(_status_repo)
        status = usecase.execute(product_id)

        # None 체크 (상태가 없으면 새로 생성)
        if status is None:
            print(f"[INFO] 상태 없음, 기본값(idle) 반환")
            from review.domain.entity.crawling_status import CrawlingStatus
            status = CrawlingStatus.create_new(product_id)

        print(f"[INFO] 상태 반환: {status.status.value}, 진행률: {status.progress}%")

        return CollectionStatusResponse(
            product_id=status.product_id,
            status=status.status.value,
            progress=status.progress,
            started_at=status.started_at,
            completed_at=status.completed_at,
            error_message=status.error_message,
            total_reviews=status.total_reviews
        )

    except Exception as e:
        print(f"[ERROR] 상태 조회 중 에러: {e}")
        import traceback
        traceback.print_exc()

        # 에러 발생 시 기본 상태 반환 (500 에러 방지)
        from review.domain.entity.crawling_status import CrawlingStatus
        status = CrawlingStatus.create_new(product_id)

        return CollectionStatusResponse(
            product_id=status.product_id,
            status=status.status.value,
            progress=0,
            started_at=None,
            completed_at=None,
            error_message=str(e),
            total_reviews=None
        )