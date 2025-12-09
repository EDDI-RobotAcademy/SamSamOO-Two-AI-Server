from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from samsam_danawa.domain.product import DanawaProduct
from samsam_danawa.domain.review import DanawaReview

# 🔎 다나와 상품 검색 (수정된 버전)
def get_image_url(img_el):
    if not img_el:
        return ""

    # 1) lazy-load 방식
    url = img_el.get("data-original") \
          or img_el.get("data-src") \
          or img_el.get("data-img") \
          or img_el.get("src") \
          or ""

    # 2) 프로토콜을 누락한 "//img..." 형태 → "https:" 붙이기
    if url.startswith("//"):
        url = "https:" + url

    return url


def search_danawa_products(query: str):
    url = f"https://search.danawa.com/dsearch.php?query={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    products = []

    items = soup.select("div.prod_main_info")

    for item in items:
        name_el = item.select_one(".prod_name a")
        price_el = item.select_one(".price_sect strong")
        img_el = item.select_one(".thumb_image img")

        if not name_el:
            continue

        link = name_el.get("href")
        product_id = link.split("pcode=")[-1]

        # 이미지 URL 분리 로직
        image_url = get_image_url(img_el)

        product = DanawaProduct(
            product_id=product_id,
            name=name_el.text.strip(),
            price=price_el.text.strip() if price_el else "",
            mall="다나와",
            image=image_url,
            link=link
        )

        products.append(product)

    return products


# ⭐ 다나와 리뷰 수집 (수정된 버전)
def get_danawa_reviews(product_id: str):
    url = f"https://prod.danawa.com/info/?pcode={product_id}"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#danawa-prodBlog-productOpinion-list"))
        )
    except Exception:
        time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    reviews = []
    review_items = soup.select("li.cmt_item")

    for item in review_items:
        nickname = item.select_one(".id_name strong")
        date = item.select_one(".date")
        content = item.select_one(".danawa-prodBlog-productOpinion-clazz-content")

        review = DanawaReview(
            user=nickname.text.strip() if nickname else "알 수 없음",
            date=date.text.strip() if date else "",
            text=content.text.strip() if content else "",
        )
        reviews.append(review)

    return reviews
