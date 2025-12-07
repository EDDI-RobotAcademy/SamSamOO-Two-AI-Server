import time
import random
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from datetime import datetime

from review.application.port.scraper_port import ScraperPort
from product.domain.entity.product import Product
from review.domain.entity.review import Review, ReviewPlatform

HEADLESS = True


# ⭐️ ScraperPort 상속 추가
class ElevenStScraperAdapter(ScraperPort):

    # ⭐️ ScraperPort의 fetch_reviews 구현 (limit 제거)
    def fetch_reviews(self, product: Product) -> List[Review]:

        # 11번가 전용 로직
        if product.source.value != ReviewPlatform.ELEVENST.value:
            raise ValueError(f"지원하지 않는 플랫폼: {product.source}")

        # 크롤링 함수 호출 (product_id는 int여야 함)
        try:
            product_code = int(product.source_product_id)
        except ValueError:
            raise ValueError("product_id는 11번가 상품 코드(정수)여야 합니다.")

        result = self._crawl_11st_reviews(product_code)  # ⭐️ 내부 메서드 호출

        if 'error' in result:
            print(f"[ERROR] 크롤링 오류: {result['error']}")
            return []

        reviews_data = result.get("reviews", [])

        # 도메인 엔티티로 변환하여 반환
        reviews = []
        for item in reviews_data:  # ⭐️ limit 없이 모든 리뷰 처리
            try:
                # rating 문자열 ('X점') 처리
                rating_str = item.get("rating", "0점").replace('점', '').strip()
                rating = float(rating_str)

                # date 문자열 처리 (11번가는 'YYYY.MM.DD' 형식으로 가정)
                date_text = item.get("date", datetime.utcnow().strftime('%Y.%m.%d'))
                if date_text == "날짜 정보 없음":
                    review_at = datetime.utcnow()
                else:
                    review_at = datetime.strptime(date_text, '%Y.%m.%d')

                review_entity = Review.create_from_crawler(
                    product_id=str(product_code),  # ⭐️ ORM과 통일하기 위해 str로 저장
                    platform=product.source,
                    content=item["content"],
                    reviewer=item["user_id"],
                    rating=rating,
                    review_at=review_at
                )
                reviews.append(review_entity)
            except Exception as e:
                print(f"[WARNING] 리뷰 엔티티 변환 실패: {e} / Data: {item}")
                continue

        return reviews

    # ⭐️ 기존 crawl_11st_reviews 함수를 내부 인스턴스 메서드로 변경
    def _crawl_11st_reviews(self, product_code: int) -> Dict[str, Any]:
        url = f"https://www.11st.co.kr/products/{product_code}"
        all_reviews: List[Dict[str, str]] = []
        store_name: Optional[str] = None
        product_title: Optional[str] = None

        IFRAME_SELECTOR = '#ifrmReview'
        REVIEWS_CONTAINER = '#review-list-page-area'
        LOAD_MORE_BUTTON_SELECTOR = 'button.c_product_btn_more8'
        STORE_NAME_SELECTOR = 'a[data-log-actionid-label="store_go"]'
        TITLE_SELECTOR = 'h1.title'
        REVIEW_ITEM_SELECTOR = f'{REVIEWS_CONTAINER} li.review_list_element'
        MORE_TEXT_BUTTON_SELECTOR = f'{REVIEWS_CONTAINER} button.review-expand-open-text'

        print(f"--- 11번가 리뷰 크롤링 시작 (Playwright) ---")
        print(f"--- 대상 URL: {url} ---")

        browser = None

        try:
            with sync_playwright() as p:
                # 1. 브라우저 시작 (Chromium 사용)
                browser = p.chromium.launch(headless=HEADLESS)
                page = browser.new_page()

                # 2. 타임아웃 설정
                page.set_default_navigation_timeout(30000)
                page.set_default_timeout(20000)

                # 3. URL 접속
                page.goto(url)
                page.wait_for_load_state("networkidle")

                # 상품명/상호명 추출
                try:
                    product_title = page.locator(TITLE_SELECTOR).text_content(timeout=10000).strip()
                    store_name = page.locator(STORE_NAME_SELECTOR).text_content(timeout=10000).strip()
                    print(f"[INFO] 상품명/상호명 추출 성공: {product_title[:15]}... / {store_name}")
                except PWTimeout:
                    print("[WARNING] 상품명 또는 상호명을 찾지 못했습니다.")

                # 4. 리뷰 탭 클릭
                REVIEW_TAB_SELECTOR = 'button[aria-controls="tabpanelDetail2"]:has-text("리뷰")'
                try:
                    review_tab = page.locator(REVIEW_TAB_SELECTOR)
                    review_tab.scroll_into_view_if_needed()
                    review_tab.click()
                    print("[INFO] 리뷰 탭 클릭 성공. iframe 로드 대기.")
                    time.sleep(random.uniform(4, 6))
                except PWTimeout:
                    print("[ERROR] 리뷰 탭을 찾지 못했습니다.")
                    return {"error": "리뷰 탭 로드 실패"}

                # 5. iframe 전환 (FrameLocator 확보)
                try:
                    review_frame_locator = page.frame_locator(IFRAME_SELECTOR)
                    print("[INFO] iframe 전환 성공. 리뷰 목록 로드 대기.")
                except Exception:
                    print(f"[FATAL ERROR] iframe ({IFRAME_SELECTOR})을 찾지 못했습니다.")
                    return {"error": "iframe 전환 실패"}

                # 6. '리뷰 더보기' 버튼 반복 클릭 루프 (모든 리뷰 로드)
                while True:
                    print(f">>> 리뷰 로딩 중... (현재 수집된 리뷰 수: {len(all_reviews)}개)")

                    try:
                        more_button = review_frame_locator.locator(LOAD_MORE_BUTTON_SELECTOR)

                        if more_button.is_visible(timeout=10000) and more_button.is_enabled():
                            more_button.click(timeout=10000)
                            print("[INFO] '리뷰 더보기' 버튼 클릭 성공. 추가 리뷰 로드 대기.")
                            time.sleep(random.uniform(5, 8))
                        else:
                            print("[INFO] '리뷰 더보기' 버튼이 비활성화되었습니다. (모든 리뷰 로드 완료)")
                            break
                    except PWTimeout:
                        print("[INFO] '리뷰 더보기' 버튼을 찾지 못했습니다. (모든 리뷰 로드 완료)")
                        break
                    except Exception as e:
                        print(f"[WARNING] '리뷰 더보기' 클릭 중 오류 발생: {e}. 루프 종료.")
                        break

                # 7. 개별 리뷰 '더보기' 버튼 클릭 (긴 리뷰 전체 내용 확보)
                print(">>> 전체 리뷰 데이터 추출 시작...")
                try:
                    more_text_buttons = review_frame_locator.locator(MORE_TEXT_BUTTON_SELECTOR).all()
                    if more_text_buttons:
                        print(f"  [INFO] 긴 리뷰 '더보기' 버튼 {len(more_text_buttons)}개 발견. 클릭 시도...")
                        for button in more_text_buttons:
                            try:
                                if button.is_visible(timeout=1000) and button.is_enabled():
                                    button.click(timeout=1000)
                            except Exception:
                                pass
                        print("  [INFO] 모든 긴 리뷰 '더보기' 버튼 클릭 완료.")
                        time.sleep(1)
                    else:
                        print("  [INFO] 긴 리뷰 '더보기' 버튼을 찾지 못했습니다.")
                except Exception as e:
                    print(f"  [WARNING] 개별 리뷰 '더보기' 클릭 로직 오류 발생: {e}")

                # 8. BeautifulSoup으로 전체 리뷰 데이터 파싱
                iframe_html = review_frame_locator.locator('body').inner_html()
                soup = BeautifulSoup(iframe_html, 'html.parser')
                # ⭐️ 기존 리뷰 목록 전체를 다시 파싱합니다. (이전 수집된 all_reviews는 무시)
                reviews = soup.select(REVIEW_ITEM_SELECTOR)

                for review in reviews:
                    try:
                        content_tag = review.select_one('p.cont_review_hide.text-expanded')
                        content = content_tag.get_text('\n', strip=True) if content_tag else "리뷰 내용 없음"

                        if content.strip() == "리뷰 내용 없음":
                            continue

                        user_id_tag = review.select_one('dl.c_product_reviewer dt.name')
                        # data-nick 속성이나, 텍스트를 사용
                        user_id = user_id_tag.get('data-nick', user_id_tag.text).strip() if user_id_tag else "ID_ERROR"

                        # 평점 'X점'에서 숫자만 추출
                        rating_text = review.select_one('p.grade em').text.strip().replace('점', '')

                        option_tag = review.select_one('dl.option_set dd')
                        option = option_tag.text.strip() if option_tag else "옵션 정보 없음"
                        date_tag = review.select_one('p.side span.date')
                        date_text = date_tag.text.strip() if date_tag else "날짜 정보 없음"

                        all_reviews.append({
                            "product_title": product_title,
                            "store_name": store_name,
                            "user_id": user_id,
                            "rating": rating_text,  # 숫자만 남긴 문자열
                            "option": option,
                            "content": content,
                            "date": date_text
                        })
                    except Exception as e:
                        print(f"  [WARNING] 개별 리뷰 추출 실패: {e}")
                        continue

                browser.close()

        except Exception as e:
            print(f"[FATAL ERROR] 크롤링 중 치명적인 오류 발생: {e}")
            if browser:
                try:
                    browser.close()
                except Exception:
                    pass

        return {"count": len(all_reviews), "reviews": all_reviews, "store_name": store_name,
                "product_title": product_title}