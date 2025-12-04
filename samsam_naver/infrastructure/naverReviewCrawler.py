# naver_review_playwright.py

from playwright.async_api import async_playwright

async def fetch_reviews(catalog_id):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        url = f"https://search.shopping.naver.com/catalog/{catalog_id}"
        await page.goto(url, timeout=30000)
        await page.wait_for_load_state("networkidle")

        # 팝업 닫기 (있다면)
        try:
            await page.click("button[class*=close]", timeout=2000)
        except:
            pass

        # ⭐ 스크롤을 여러 번 내려서 리뷰 영역 완전 로딩
        for _ in range(5):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1200)

        # ⭐ 실제 리뷰 영역 선택자 (2024~2025 기준)
        await page.wait_for_selector("ul[class*=review_list__]", timeout=10000)

        review_items = await page.query_selector_all("ul[class*=review_list__] li")

        data = []
        for item in review_items:
            # 리뷰 텍스트 가져오기
            text = await item.inner_text()
            data.append(text.strip())

        await browser.close()
        return data
