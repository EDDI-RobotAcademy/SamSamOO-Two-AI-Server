from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

class NaverCrawler:

    @staticmethod
    def get_reviews(catalog_id: str, page: int = 1):
        url = f"https://search.shopping.naver.com/catalog/{catalog_id}/review?page={page}"

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        time.sleep(2)

        review_elements = driver.find_elements(By.CSS_SELECTOR, ".reviewItems_text__XIsTc")

        reviews = [r.text.strip() for r in review_elements]

        driver.quit()
        return reviews
