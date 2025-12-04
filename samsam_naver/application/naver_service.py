from samsam_naver.infrastructure.naver_api import search_api
from samsam_naver.infrastructure.naver_review_playwright import fetch_reviews


async def search_products(query: str):
    return search_api(query)


async def get_reviews(catalog_id: str):
    return await fetch_reviews(catalog_id)
