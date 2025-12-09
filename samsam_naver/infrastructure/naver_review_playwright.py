import asyncio
from playwright.async_api import async_playwright

async def fetch_reviews(catalog_id: str):
    url = f"https://smartstore.naver.com/brands/products/{catalog_id}"
    api_url = "https://smartstore.naver.com/i/v1/reviews/paged-reviews"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        reviews_data = None

        # XHR 요청 인터셉트
        async def handle_response(response):
            nonlocal reviews_data
            if api_url in response.url:
                if response.status == 200:
                    reviews_data = await response.json()

        page.on("response", handle_response)

        # 제품 페이지 진입 (리뷰 XHR 자동 발생)
        await page.goto(url, wait_until="networkidle")

        # XHR이 올 때까지 대기
        for _ in range(10):
            if reviews_data:
                break
            await asyncio.sleep(0.3)

        await browser.close()

        if reviews_data is None:
            raise Exception("리뷰 API 응답을 받지 못했습니다. catalog_id를 다시 확인하세요.")

        return reviews_data


async def get_reviews(catalog_id: str):
    return await fetch_reviews(catalog_id)
