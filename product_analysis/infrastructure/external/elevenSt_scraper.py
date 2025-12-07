import time
import random
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

HEADLESS = True

class ElevenStScraperAdapter:

    def crawl_11st_reviews(product_code: int) -> Dict[str, Any]:
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
                    # Playwright는 .text_content()를 사용합니다.
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
                    # iframe 로드 시간 대기
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

                # 6. '리뷰 더보기' 버튼 반복 클릭 루프
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
                    # iframe 내부에서 모든 '더보기' 버튼을 찾습니다.
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
                # ⭐️⭐️⭐️ [핵심 수정 1]: FrameLocator에서 .inner_html()을 사용하여 HTML 내용 추출 ⭐️⭐️⭐️
                # iframe의 body 태그의 내부 HTML을 가져옵니다.
                iframe_html = review_frame_locator.locator('body').inner_html()
                soup = BeautifulSoup(iframe_html, 'html.parser')
                reviews = soup.select(REVIEW_ITEM_SELECTOR)

                for review in reviews:
                    try:
                        content_tag = review.select_one('p.cont_review_hide.text-expanded')
                        content = content_tag.get_text('\n', strip=True) if content_tag else "리뷰 내용 없음"

                        if content.strip() == "리뷰 내용 없음":
                            continue

                        # 데이터 추출 (BeautifulSoup 사용)
                        user_id_tag = review.select_one('dl.c_product_reviewer dt.name')
                        user_id = user_id_tag.get('data-nick', user_id_tag.text).strip() if user_id_tag else "ID_ERROR"
                        rating_text = review.select_one('p.grade em').text.strip()
                        option_tag = review.select_one('dl.option_set dd')
                        option = option_tag.text.strip() if option_tag else "옵션 정보 없음"
                        date_tag = review.select_one('p.side span.date')
                        date_text = date_tag.text.strip() if date_tag else "날짜 정보 없음"

                        all_reviews.append({
                            "product_title": product_title,
                            "store_name": store_name,
                            "page": "Loaded",
                            "user_id": user_id,
                            "rating": f"{rating_text}점",
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
            # 오류 발생 시 브라우저가 아직 열려있다면 닫아줍니다.
            if browser:
                try:
                    browser.close()
                except Exception:
                    pass

        return {"count": len(all_reviews), "reviews": all_reviews, "store_name": store_name, "product_title": product_title}