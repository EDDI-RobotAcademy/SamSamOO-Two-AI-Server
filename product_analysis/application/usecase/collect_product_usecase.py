from typing import List
from product.application.port.product_repository_port import ProductRepositoryPort
from product_analysis.application.port.review_repository_port import ReviewRepositoryPort
from product_analysis.application.port.scraper_port import ScraperPort
from product.domain.entity.product import Product
from product_analysis.domain.entity.review import Review


class CollectProductUseCase:

    def __init__(self, scraper: ScraperPort, product_repo: ProductRepositoryPort, review_repo: ReviewRepositoryPort):
        self.scraper = scraper
        self.product_repo = product_repo
        self.review_repo = review_repo

    def execute(self, keyword: str, limit_products: int, limit_reviews: int) -> List[Product]:

        # 1. 스크래퍼를 통해 외부 플랫폼에서 상품 목록 검색
        products: List[Product] = self.scraper.search_products(keyword, limit_products)
        saved: List[Product] = []

        for p in products:
            # 2. 중복 체크 (변경됨: item_code 대신 (source, title) 기반 조회)
            # find_by_item_code 대신 find_by_title을 사용합니다.
            exist = self.product_repo.find_by_title(p.source, p.title)

            if exist:
                # 이미 존재하는 경우: 기존 상품 정보 사용 (ID 포함)
                prod = exist
                print(f"[INFO] 상품 '{prod.title[:15]}...' (ID: {prod.id})는 이미 존재하여 재수집합니다.")
            else:
                # 신규 상품인 경우: DB에 저장
                prod = self.product_repo.save(p)
                print(f"[INFO] 신규 상품 '{prod.title[:15]}...' (ID: {prod.id})를 DB에 저장했습니다.")

            # 3. 리뷰 수집 (상품 ID를 포함한 prod 엔티티 사용)
            try:
                reviews: List[Review] = self.scraper.fetch_reviews(prod, limit_reviews)

                # 4. 리뷰 엔티티에 DB ID 할당
                for r in reviews:
                    r.product_id = prod.id

                # 5. 리뷰 DB에 저장
                if reviews:
                    self.review_repo.save_all(reviews)
                    print(f"[INFO] 총 {len(reviews)}개의 리뷰를 수집 및 저장했습니다.")
                else:
                    print("[INFO] 수집된 리뷰가 없습니다.")

            except Exception as e:
                print(f"[ERROR] 리뷰 수집 중 오류 발생 (상품 ID: {prod.id}): {e}")

            saved.append(prod)

        return saved