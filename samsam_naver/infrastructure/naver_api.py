import requests
from config.env_loader import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
from samsam_naver.domain.product import Product
from samsam_naver.infrastructure.naver_crawler import extract_catalog_id


def search_api(query: str):
    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": 10}

    res = requests.get(url, headers=headers, params=params)
    data = res.json()

    items = []
    for item in data.get("items", []):
        items.append(
            Product(
                product_id=item.get("productId"),
                name=item.get("title"),
                price=item.get("lprice"),
                mall=item.get("mallName"),
                image=item.get("image"),
                link=item.get("link"),
                catalog_id=extract_catalog_id(item.get("link"))
            ).to_dict()
        )

    return items
