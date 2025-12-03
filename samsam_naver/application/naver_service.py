from samsam_naver.infrastructure.naver_review_playwright import get_reviews as playwright_reviews

class NaverService:

    @staticmethod
    async def search_products(query: str):
        from samsam_naver.infrastructure.naver_api import search_products
        return search_products(query)

    @staticmethod
    async def get_reviews(catalog_id: str):
        return await playwright_reviews(catalog_id)
