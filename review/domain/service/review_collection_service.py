from typing import List
from review.domain.entity.review import Review
from review.domain.entity.crawling_status import CrawlingStatus
from review.infrastructure.repository.crawling_status_repository import CrawlingStatusRepository
from product.domain.entity.product import Product


class ReviewCollectionService:
    """리뷰 수집 도메인 서비스"""

    def __init__(
            self,
            scraper,  # ScraperPort
            review_repository,  # ReviewRepository
            status_repository: CrawlingStatusRepository  # ⭐️ DB Repository
    ):
        self.scraper = scraper
        self.review_repository = review_repository
        self.status_repository = status_repository

    def collect_and_save_reviews(self, product: Product) -> dict:
        """리뷰 수집 및 저장"""
        product_id = product.source_product_id

        # 1. 기존 상태 조회 또는 생성
        status = self.status_repository.find_by_product_id(product_id)
        if status is None:
            status = CrawlingStatus.create_new(product_id)

        # 2. 수집 가능 여부 확인
        if not status.can_start_collecting():
            raise ValueError(f"현재 상태({status.status})에서는 수집을 시작할 수 없습니다")

        try:
            # 3. 수집 시작
            status.start_collecting()
            self.status_repository.save(status)
            print(f"[INFO] 리뷰 수집 시작: {product_id}")

            # 4. 크롤링 실행
            reviews = self.scraper.fetch_reviews(product)
            total = len(reviews)
            print(f"[INFO] {total}개 리뷰 크롤링 완료")

            # 5. 리뷰 저장 + 진행률 업데이트
            for idx, review in enumerate(reviews, 1):
                self.review_repository.save(review)

                # 10개마다 또는 마지막에 진행률 업데이트
                if idx % 10 == 0 or idx == total:
                    progress = int((idx / total) * 100)
                    status.update_progress(progress)
                    self.status_repository.save(status)
                    print(f"[INFO] 저장 진행률: {progress}%")

            # 6. 수집 완료
            status.complete_collecting(total)
            self.status_repository.save(status)
            print(f"[SUCCESS] 리뷰 수집 완료: {total}개")

            return {
                "status": "success",
                "total_reviews": total,
                "product_id": product_id
            }

        except Exception as e:
            # 7. 실패 처리
            status.mark_failed(str(e))
            self.status_repository.save(status)
            print(f"[ERROR] 리뷰 수집 실패: {str(e)}")
            raise

    def get_collection_status(self, product_id: str) -> CrawlingStatus:
        """수집 상태 조회"""
        status = self.status_repository.find_by_product_id(product_id)
        if status is None:
            # 상태가 없으면 새로 생성
            status = CrawlingStatus.create_new(product_id)
        return status

    def start_analyzing(self, product_id: str) -> None:
        """분석 시작"""
        status = self.status_repository.find_by_product_id(product_id)
        if status is None or not status.can_start_analyzing():
            raise ValueError("분석을 시작할 수 없습니다")

        status.start_analyzing()
        self.status_repository.save(status)