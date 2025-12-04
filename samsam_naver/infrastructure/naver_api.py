import re
import requests
from config.env_loader import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET


def extract_catalog_id(url: str):
    """
    네이버 쇼핑 상품 상세 URL에서 catalogId(nvMid)를 추출
    예: https://smartstore.naver.com/.../products/12345678 → 12345678
    """
    if not url:
        return None

    # 패턴 1: /catalog/숫자
    match = re.search(r'/catalog/(\d+)', url)
    if match:
        return match.group(1)

    # 패턴 2: /product 또는 /products/숫자
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
    params = {
        "query": query,
        "display": 10,
    }

    resp = requests.get(url, headers=headers, params=params)

    if resp.status_code != 200:
        raise Exception(f"네이버 API 오류 발생: {resp.status_code}")

    data = resp.json()
    result = []

    for item in data.get("items", []):
        result.append({
            "productId": item.get("productId"),
            "name": re.sub(r"<.*?>", "", item.get("title", "")),  # HTML 태그 제거
            "price": int(item.get("lprice", 0)),
            "mall": item.get("mallName"),
            "image": item.get("image"),
            "link": item.get("link"),
            "catalogId": extract_catalog_id(item.get("link")),
        })

    return result
