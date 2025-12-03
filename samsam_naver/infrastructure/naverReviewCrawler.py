# naver_review_playwright.py
from playwright.async_api import async_playwright


async def fetch_reviews(catalog_id):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(f"https://search.shopping.naver.com/catalog/{catalog_id}")
        await page.wait_for_load_state("networkidle")

        # 팝업 닫기 (있을 때만)
        try:
            await page.click("button[class*=close]", timeout=2000)
        except:
            pass

        # 스크롤
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1500)

        # 더 안정적인 리뷰 선택자
        await page.wait_for_selector("div[class*=reviewItems]", timeout=10000)

        reviews = await page.query_selector_all("div[class*=reviewItems_list_review]")

        data = []
        for r in reviews:
            text = await r.inner_text()
            data.append(text)

        await browser.close()
        return data
