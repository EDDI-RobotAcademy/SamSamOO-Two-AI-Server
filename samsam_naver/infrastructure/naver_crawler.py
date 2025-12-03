import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from typing import List

from samsam_naver.domain.product import Product
from samsam_naver.domain.review import Review

HEADERS = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
}

class NaverCrawler:
    @staticmethod
    def search_products(query: str) -> List[Product]:
        encoded = quote(query)
        url = f"https://search.shopping.naver.com/search/all?query={encoded}"

        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        products = []
        items = soup.select(".product_item")  # DOM 구조 맞게 직접 수정 필요

        for idx, item in enumerate(items, start=1):
            name_el = item.select_one(".product_link")
            price_el = item.select_one(".price_num")
            mall_el = item.select_one(".mall_name")

            if not name_el or not price_el:
                continue

            name = name_el.get_text(strip=True)
            price = int(price_el.get_text(strip=True)
                        .replace(",", "")
                        .replace("원", ""))

            mall = mall_el.get_text(strip=True) if mall_el else None

            products.append(
                Product(
                    id=str(idx),
                    name=name,
                    price=price,
                    mall_name=mall
                )
            )
        return products

    @staticmethod
    def get_reviews(product: Product) -> List[Review]:
        # 실제 리뷰 페이지 구조에 맞게 작성 필요
        return []
