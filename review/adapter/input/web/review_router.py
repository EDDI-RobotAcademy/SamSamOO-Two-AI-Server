from fastapi import APIRouter

from product.domain.entity.product import Product
from review.adapter.input.web.response.crawl_review_response import ReviewFetchResponse, ReviewItem  # ReviewItem 추가
from review.application.usecase.fetch_review_usecase import FetchReviewsUseCase
from review.application.port.scraper_factory import get_scraper_adapter
from review.infrastructure.repository.review_repository_impl import ReviewRepositoryImpl
from review.adapter.input.web.request.crawl_review_request import FetchReviewsRequest

_review_repo = ReviewRepositoryImpl()

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