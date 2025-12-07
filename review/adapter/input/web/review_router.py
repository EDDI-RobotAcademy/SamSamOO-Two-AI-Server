from fastapi import APIRouter

from product.domain.entity.product import Product
from review.adapter.input.web.response.crawl_review_response import ReviewFetchResponse, ReviewItem  # ReviewItem 추가
from review.application.usecase.fetch_review_usecase import FetchReviewsUseCase
from review.infrastructure.external.elevenSt_scraper import ElevenStScraperAdapter
from review.infrastructure.repository.review_repository_impl import ReviewRepositoryImpl
from review.adapter.input.web.request.crawl_review_request import FetchReviewsRequest

_review_repo = ReviewRepositoryImpl()
_scraper_adapter = ElevenStScraperAdapter()
review_uc = FetchReviewsUseCase(_scraper_adapter, _review_repo)

review_router = APIRouter(tags=["review"])


@review_router.post("/crawl", response_model=ReviewFetchResponse)
def fetch_reviews(req: FetchReviewsRequest):
    # ⭐️ Product 생성자를 직접 호출하는 대신 팩토리 메서드 사용 ⭐️
    product = Product.create_for_crawl_request(
        platform=req.platform,
        product_id=str(req.product_id)  # req.product_id가 int이므로 str로 변환
    )

    reviews = review_uc.execute(product)

    review_items = []
    product_name = "N/A"

    for r in reviews:  # r: Review 엔티티
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