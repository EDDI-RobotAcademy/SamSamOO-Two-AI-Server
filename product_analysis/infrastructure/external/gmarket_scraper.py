import os
from datetime import datetime
from typing import List
from product_analysis.application.port.scraper_port import ScraperPort
from product_analysis.domain.entity.product import Product
from product_analysis.domain.entity.review import Review

USE_PLAYWRIGHT = os.getenv("USE_PLAYWRIGHT", "false").lower() == "true"  # 기본 false로!

class GmarketScraper(ScraperPort):
    def __init__(self):
        self.use_pw = USE_PLAYWRIGHT

    def search_products(self, keyword: str, limit: int) -> List[Product]:
        # 1) 개발 중에는 기본적으로 더미로 즉시 응답
        if not self.use_pw:
            print("[GmarketScraper] USE_PLAYWRIGHT = false -> dummy products")
            return self._dummy_products(keyword, limit)

        try:
            from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
            from bs4 import BeautifulSoup

            with sync_playwright() as p:
                # 2) 채널 우선(설치된 Edge/Chrome), 실패 시 기본 chromium
                try:
                    browser = p.chromium.launch(channel="msedge", headless=True)
                except Exception:
                    browser = p.chromium.launch(headless=True)

                page = browser.new_page()
                # 3) 하드 타임아웃(15초) + 네비게이션 대기 상태 최소화
                page.set_default_navigation_timeout(15000)
                page.goto(f"https://browse.gmarket.co.kr/search?keyword={keyword}", timeout=15000)
                page.wait_for_load_state("domcontentloaded", timeout=10000)

                html = page.content()
                browser.close()

            soup = BeautifulSoup(html, "html.parser")
            items: List[Product] = []
            for i, card in enumerate(soup.select("div.box__component-itemcard"), start=1):
                title_el = card.select_one(".text__item")
                link_el  = card.select_one("a.link__item")
                price_el = card.select_one(".text__value")
                rev_el   = card.select_one(".text__review-count")

                if not (title_el and link_el):
                    continue

                title = title_el.get_text(strip=True)
                url   = link_el["href"]
                price = self._parse_price(price_el.text if price_el else None)
                review_count = self._parse_int(rev_el.text) if rev_el else 0

                items.append(Product(
                    id=None, source="gmarket",
                    item_code=f"GM-{keyword}-{i}",
                    title=title, price=price, seller="G마켓 스토어",
                    rating=None, review_count=review_count,
                    url=url, collected_at=datetime.now()
                ))
                if len(items) >= limit:
                    break

            print(f"[GmarketScraper] scraped {len(items)} items")
            return items

        except Exception as e:
            # 4) 어떤 이유로든 실패하면 즉시 더미로 폴백 (핵심)
            print(f"[GmarketScraper] Playwright error -> fallback to dummy: {e}")
            return self._dummy_products(keyword, limit)

    def fetch_reviews(self, product: Product, limit: int) -> List[Review]:
        if not self.use_pw:
            print("[GmarketScraper] USE_PLAYWRIGHT = false -> dummy reviews")
            return self._dummy_reviews(product, limit)
        try:
            # TODO: 실제 리뷰 탭 파싱 (필요시 page.set_default_xxx_timeout 적용)
            return self._dummy_reviews(product, limit)
        except Exception as e:
            print(f"[GmarketScraper] fetch_reviews error -> dummy: {e}")
            return self._dummy_reviews(product, limit)

    # ---------- helpers ----------
    def _parse_price(self, s: str | None) -> int | None:
        if not s: return None
        digits = "".join(ch for ch in s if ch.isdigit())
        return int(digits) if digits else None

    def _parse_int(self, s: str | None) -> int:
        if not s: return 0
        digits = "".join(ch for ch in s if ch.isdigit())
        return int(digits) if digits else 0

    def _dummy_products(self, keyword: str, limit: int) -> List[Product]:
        return [
            Product(
                id=None, source="gmarket", item_code=f"GM-{keyword}-{i}",
                title=f"[G마켓] {keyword} 상품 {i}",
                price=10000 + i * 1000, seller="G마켓 스토어",
                rating=None, review_count=100 + i,
                url=f"https://www.gmarket.co.kr/item?goodscode=dummy-{i}",
                collected_at=datetime.now()
            ) for i in range(limit)
        ]

    def _dummy_reviews(self, product: Product, limit: int) -> List[Review]:
        return [
            Review(
                id=None, product_id=None, rating=5 if i % 2 == 0 else 3,
                content=(f"{product.title} 배송 빠르고 가성비 좋아요! {i}"
                         if i % 2 == 0 else
                         f"{product.title} 품질이 별로고 포장이 아쉬움 {i}"),
                written_at=datetime.now(), collected_at=datetime.now()
            ) for i in range(limit)
        ]
