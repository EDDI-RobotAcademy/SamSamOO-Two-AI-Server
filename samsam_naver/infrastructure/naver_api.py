import re
import requests
from config.env_loader import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

def extract_catalog_id(url: str):
    """
    네이버 쇼핑 상품 상세 URL에서 catalogId(nvMid) 추출
    """
    if not url:
        return None

    # /catalog/1234567890
    match = re.search(r'/catalog/(\d+)', url)
    if match:
        return match.group(1)

    # /products/1234567890
    match = re.search(r'/products?/(\d+)', url)
    if match:
        return match.group(1)

    return None


def search_products(query: str):
    """
    네이버 쇼핑 API 상품 검색
    """
    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": 10}

    resp = requests.get(url, headers=headers, params=params)

    if resp.status_code != 200:
        raise Exception(f"네이버 API 오류: {resp.status_code}")

    data = resp.json()

    items = []
    for item in data.get("items", []):
        items.append({
            "productId": item.get("productId"),
            "name": item.get("title"),
            "price": item.get("lprice"),
            "mall": item.get("mallName"),
            "image": item.get("image"),
            "link": item.get("link"),
            "catalogId": extract_catalog_id(item.get("link")),
        })

    return items
