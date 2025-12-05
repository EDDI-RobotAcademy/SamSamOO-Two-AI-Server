import asyncio
from playwright.async_api import async_playwright

async def fetch_reviews(catalog_id: str):
    url = f"https://smartstore.naver.com/brands/products/{catalog_id}"
    api_url = "https://smartstore.naver.com/i/v1/reviews/paged-reviews"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        reviews_data = None

        async def on_response(response):
            nonlocal reviews_data
            if api_url in response.url and response.status == 200:
                reviews_data = await response.json()

        page.on("response", on_response)

        await page.goto(url, wait_until="networkidle")

        for _ in range(20):
            if reviews_data:
                break
            await asyncio.sleep(0.3)

        await browser.close()

        if not reviews_data:
            raise Exception("리뷰 데이터를 가져올 수 없습니다. catalog_id를 확인하세요.")

        return reviews_data.get("contents", [])
