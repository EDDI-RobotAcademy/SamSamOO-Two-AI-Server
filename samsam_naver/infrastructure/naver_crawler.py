from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class NaverCrawler:

    @staticmethod
    def get_reviews(catalog_id: str, page: int = 1):
        url = f"https://search.shopping.naver.com/catalog/{catalog_id}/review?page={page}"

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # ⭐ User-Agent 추가 (차단 방지)
        chrome_options.add_argument(
            "User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        time.sleep(2)

        # ⭐ "reviewItems_text" 클래스를 포함하는 요소 패턴 기반 검색
        selector = "div[class*='reviewItems_text']"

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
            )
        except:
            print("[WARN] 리뷰 요소를 찾을 수 없습니다.")
            driver.quit()
            return []

        # 스크롤 끝까지 내려서 추가 리뷰 로딩(선택)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        review_elements = driver.find_elements(By.CSS_SELECTOR, selector)
        reviews = [r.text.strip() for r in review_elements if r.text.strip()]

        driver.quit()
        return reviews
