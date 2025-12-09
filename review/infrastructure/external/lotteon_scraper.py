"""
Lotteon Scraper Adapter
롯데온 리뷰 크롤러 어댑터 (Playwright 기반)
"""
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


class LotteonScraper(ScraperPort):
    """
    롯데온 리뷰 스크래퍼
    ScraperPort를 구현하여 롯데온 플랫폼의 리뷰를 크롤링
    """

    def fetch_reviews(self, product: Product) -> List[Review]:
        """
        롯데온 상품의 리뷰를 크롤링하여 반환

        Args:
            product: 상품 엔티티 (source, source_product_id 포함)

        Returns:
            List[Review]: 크롤링된 리뷰 엔티티 리스트
        """
        # 롯데온 전용 로직
        if product.source.value != ReviewPlatform.LOTTEON.value:
            raise ValueError(f"지원하지 않는 플랫폼: {product.source}")

        # 상품 ID 검증
        product_code = product.source_product_id.strip()
        if not product_code:
            raise ValueError("product_id가 비어있습니다.")

        print(f"[INFO] 롯데온 상품 크롤링 시작: {product_code}")

        # 크롤링 실행
        result = self._crawl_lotteon_reviews(product_code)

        if 'error' in result:
            print(f"[ERROR] 크롤링 오류: {result['error']}")
            return []

        reviews_data = result.get("reviews", [])
        print(f"[INFO] 총 {len(reviews_data)}개의 리뷰 수집 완료")

        # 도메인 엔티티로 변환
        reviews = []
        for item in reviews_data:
            try:
                # rating 처리 (별점, 숫자)
                rating_value = item.get("rating", 5.0)
                if isinstance(rating_value, str):
                    # '5점', '5.0' 등의 문자열 처리
                    rating_value = float(rating_value.replace('점', '').replace('★', '').strip())
                rating = float(rating_value)

                # date 처리
                date_text = item.get("date", "")
                if not date_text or date_text == "날짜 정보 없음":
                    review_at = datetime.utcnow()
                else:
                    review_at = self._parse_date(date_text)

                # Review 엔티티 생성
                review_entity = Review.create_from_crawler(
                    product_id=product_code,
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

    def _parse_date(self, date_text: str) -> datetime:
        """
        다양한 날짜 형식을 파싱
        예: '2024.01.15', '2024-01-15', '24.01.15'
        """
        date_text = date_text.strip()

        # 시도할 날짜 형식들
        date_formats = [
            '%Y.%m.%d',
            '%Y-%m-%d',
            '%y.%m.%d',
            '%Y/%m/%d',
            '%Y년 %m월 %d일'
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_text, fmt)
            except ValueError:
                continue

        # 파싱 실패 시 현재 시간 반환
        print(f"[WARNING] 날짜 파싱 실패: {date_text}, 현재 시간 사용")
        return datetime.utcnow()

    def _crawl_lotteon_reviews(self, product_code: str) -> Dict[str, Any]:
        """
        롯데온 리뷰 크롤링 메인 로직

        Args:
            product_code: 롯데온 상품 코드 (예: LO2352433507)

        Returns:
            Dict: 크롤링 결과 {'count': int, 'reviews': List[Dict], ...}
        """
        # 롯데온 상품 URL 생성
        url = f"https://www.lotteon.com/p/product/{product_code}"
        all_reviews: List[Dict[str, str]] = []
        product_title: Optional[str] = None
        brand_name: Optional[str] = None

        print(f"--- 롯데온 리뷰 크롤링 시작 (Playwright) ---")
        print(f"--- 대상 URL: {url} ---")

        browser = None

        try:
            with sync_playwright() as p:
                # 1. 브라우저 시작
                browser = p.chromium.launch(headless=HEADLESS)
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()

                # 2. 타임아웃 설정
                page.set_default_navigation_timeout(60000)
                page.set_default_timeout(30000)

                # 3. URL 접속
                print(f"[INFO] 페이지 로딩 중...")
                try:
                    page.goto(url, wait_until="domcontentloaded")
                except Exception as e:
                    print(f"[ERROR] 페이지 로딩 실패: {e}")
                    return {"error": f"페이지 접속 실패: {e}"}

                time.sleep(random.uniform(3, 5))

                # 4. 상품명/브랜드 추출 (다양한 셀렉터 시도)
                title_selectors = ['h2.prd_name', '.prodName', 'h1.product-title', '.product_name']
                for selector in title_selectors:
                    try:
                        elem = page.locator(selector).first
                        if elem.is_visible(timeout=3000):
                            product_title = elem.text_content().strip()
                            print(f"[INFO] 상품명: {product_title[:50]}...")
                            break
                    except:
                        continue

                brand_selectors = ['.brand_name', '.prd_brand', '.product-brand', 'span.brand']
                for selector in brand_selectors:
                    try:
                        elem = page.locator(selector).first
                        if elem.is_visible(timeout=3000):
                            brand_name = elem.text_content().strip()
                            print(f"[INFO] 브랜드: {brand_name}")
                            break
                    except:
                        continue

                # 5. 리뷰 영역으로 스크롤 및 탭 클릭
                print("\n" + "="*60)
                print("[INFO] 리뷰 섹션 찾기 시작...")
                print("="*60)

                # 페이지를 천천히 스크롤 (동적 로딩 유도)
                print("[DEBUG] 페이지 스크롤 중...")
                for i in range(5):  # 3->5로 증가
                    scroll_position = (i+1) * 600
                    page.evaluate(f"window.scrollTo(0, {scroll_position})")
                    print(f"  - 스크롤 위치: {scroll_position}px")
                    time.sleep(1.5)  # 1초 -> 1.5초로 증가

                # 추가 대기 (동적 콘텐츠 로딩)
                print("[DEBUG] 동적 콘텐츠 로딩 대기 중...")
                time.sleep(3)

                # 리뷰 탭 찾아서 클릭
                review_tab_clicked = False
                tab_selectors = [
                    # 롯데온 특정 구조 (업로드된 이미지 기반)
                    'li[data-object*="tab_type=review"]',
                    'li[data-object*="reviewtab"]',
                    '[data-object*="tab_type=review"]',

                    # 일반적인 패턴
                    'a[href="#pdReview"]',
                    'a[href*="review"]',
                    'button[aria-label*="리뷰"]',

                    # 텍스트 기반
                    'li:has-text("리뷰")',
                    'a:has-text("리뷰")',
                    'button:has-text("리뷰")',
                    'li:has-text("리뷰") a',
                    'li:has-text("리뷰") button',

                    # 클래스 기반
                    '.review-tab',
                    '.tab-review',
                    '.tab_review',
                    '[data-tab="review"]',
                    '[data-tab="pdReview"]',

                    # 더 넓은 범위
                    'nav a:has-text("리뷰")',
                    'ul.tabs a:has-text("리뷰")',
                    '.product-tabs a:has-text("리뷰")',
                    '.tab-menu a:has-text("리뷰")',
                    '.scrollTabInner li:has-text("리뷰")',
                ]

                print(f"\n[DEBUG] {len(tab_selectors)}개의 리뷰 탭 셀렉터 시도 중...")

                for idx, selector in enumerate(tab_selectors, 1):
                    print(f"\n--- 시도 #{idx}: {selector} ---")
                    try:
                        tabs = page.locator(selector).all()
                        print(f"  ✓ 발견된 요소 수: {len(tabs)}개")

                        if not tabs:
                            print(f"  ✗ 요소를 찾지 못함")
                            continue

                        for tab_idx, tab in enumerate(tabs):
                            try:
                                # 요소 정보 수집
                                is_visible = tab.is_visible(timeout=1000)
                                text_content = ""
                                if is_visible:
                                    try:
                                        text_content = tab.text_content(timeout=1000)[:50]
                                    except:
                                        text_content = "텍스트 없음"
                                else:
                                    text_content = "N/A (보이지 않음)"

                                print(f"  [{tab_idx}] 가시성: {is_visible}, 텍스트: '{text_content}'")

                                # '정책' 포함 여부 확인
                                if '정책' in text_content:
                                    print(f"      → 건너뜀 ('정책' 포함)")
                                    continue

                                # '리뷰' 포함 확인 (또는 data-object에 review 포함)
                                has_review_text = '리뷰' in text_content
                                has_review_attr = False

                                # data-object 속성 확인
                                try:
                                    data_obj = tab.get_attribute('data-object')
                                    if data_obj and 'review' in data_obj.lower():
                                        has_review_attr = True
                                        print(f"      → data-object 속성에 'review' 포함: {data_obj[:30]}")
                                except:
                                    pass

                                if not has_review_text and not has_review_attr and text_content != "텍스트 없음":
                                    print(f"      → 건너뜀 ('리뷰' 미포함)")
                                    continue

                                if is_visible or text_content == "텍스트 없음" or has_review_attr:
                                    print(f"      → 클릭 시도 중...")
                                    try:
                                        # 스크롤 후 클릭
                                        tab.scroll_into_view_if_needed(timeout=2000)
                                        time.sleep(0.5)
                                        tab.click(timeout=5000, force=False)
                                        print(f"      ✓ 클릭 성공!")
                                        review_tab_clicked = True
                                        time.sleep(4)  # 클릭 후 대기 시간 증가
                                        break
                                    except Exception as click_error:
                                        print(f"      ✗ 일반 클릭 실패, JavaScript 클릭 시도...")
                                        try:
                                            # JavaScript 클릭 시도
                                            page.evaluate(f"""
                                                document.querySelectorAll('{selector}')[{tab_idx}]?.click()
                                            """)
                                            print(f"      ✓ JavaScript 클릭 성공!")
                                            review_tab_clicked = True
                                            time.sleep(4)
                                            break
                                        except:
                                            print(f"      ✗ JavaScript 클릭도 실패: {str(click_error)[:30]}...")
                                else:
                                    print(f"      → 건너뜀 (보이지 않음)")

                            except Exception as e:
                                print(f"      ✗ 요소 처리 실패: {str(e)[:50]}...")
                                continue

                        if review_tab_clicked:
                            print(f"\n★★★ 리뷰 탭 클릭 성공! (셀렉터: {selector}) ★★★")
                            break
                        else:
                            print(f"  ✗ 클릭 가능한 요소 없음")

                    except Exception as e:
                        print(f"  ✗ 에러 발생: {str(e)[:50]}...")
                        continue

                print("\n" + "="*60)
                if review_tab_clicked:
                    print("[SUCCESS] 리뷰 탭 클릭 완료")
                else:
                    print("[WARNING] 리뷰 탭을 찾지 못함 - 스크롤로 대체")
                    # 리뷰 영역까지 스크롤
                    print("[DEBUG] 페이지 하단으로 스크롤 중...")
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.6)")
                    time.sleep(2)
                print("="*60 + "\n")

                # 6. 리뷰 컨테이너가 로드될 때까지 대기
                time.sleep(3)

                # 7. 페이지네이션 처리 및 리뷰 수집
                print("[INFO] 리뷰 수집 시작...")

                # 현재 페이지(1페이지) 리뷰 먼저 수집
                all_reviews = []
                self._collect_reviews_from_current_page(page, all_reviews, product_title, brand_name)

                # 페이지네이션 확인
                print("\n[INFO] 페이지네이션 확인 중...")
                time.sleep(2)  # 리뷰 로딩 대기

                # 페이지네이션 방식 확인 (페이지 번호 우선)
                pagination_exists = False
                pagination_selectors = [
                    '.paginationArea a',
                    '.pagination a',
                    'div[class*="pagination"] a',
                    'a[data-v-e6ad9102]',
                ]

                print("[DEBUG] 페이지 번호 방식 확인 중...")
                for selector in pagination_selectors:
                    try:
                        # 숫자 "2"가 있는지 확인 (2페이지가 있다면 페이지네이션 존재)
                        page_two = page.locator(f'{selector}:has-text("2")').first
                        if page_two.is_visible(timeout=2000):
                            pagination_exists = True
                            print(f"  ✓ 페이지네이션 발견: {selector}")
                            break
                    except:
                        continue

                if pagination_exists:
                    # 페이지 번호 방식
                    print("[INFO] 페이지 번호 방식으로 리뷰 수집")

                    max_pages = 50  # 최대 50페이지까지 시도
                    failed_attempts = 0
                    max_failed_attempts = 2  # 연속 2번 실패하면 중단

                    page_num = 2
                    while page_num <= max_pages and failed_attempts < max_failed_attempts:
                        print(f"\n[INFO] 페이지 {page_num} 이동 시도...")
                        page_clicked = False

                        # 1. 먼저 페이지 번호가 직접 보이는지 확인
                        for selector in pagination_selectors:
                            try:
                                page_links = page.locator(f'{selector}:has-text("{page_num}")').all()

                                for link in page_links:
                                    try:
                                        if link.is_visible(timeout=1000):
                                            link.scroll_into_view_if_needed()
                                            link.click(timeout=3000)
                                            print(f"  ✓ 페이지 {page_num} 클릭 성공")
                                            page_clicked = True
                                            time.sleep(random.uniform(2, 3))

                                            # 이 페이지의 리뷰 수집
                                            self._collect_reviews_from_current_page(page, all_reviews, product_title, brand_name)
                                            failed_attempts = 0  # 성공 시 실패 카운트 리셋
                                            break
                                    except:
                                        continue

                                if page_clicked:
                                    break
                            except:
                                continue

                        # 2. 페이지 번호가 안 보이면 ">" (다음) 버튼 클릭
                        if not page_clicked:
                            print(f"  - 페이지 {page_num} 버튼이 보이지 않음, '다음' 버튼 시도...")

                            next_button_selectors = [
                                'a.next:has-text(">")',
                                'a:has-text(">")',
                                'button:has-text(">")',
                                '.pagination a.next',
                                'a[class*="next"]',
                                '.paginationArea a.next',
                            ]

                            next_clicked = False
                            for selector in next_button_selectors:
                                try:
                                    next_btn = page.locator(selector).first
                                    if next_btn.is_visible(timeout=1000):
                                        next_btn.scroll_into_view_if_needed()
                                        next_btn.click(timeout=3000)
                                        print(f"  ✓ '다음' 버튼 클릭 성공")
                                        next_clicked = True
                                        time.sleep(random.uniform(2, 3))

                                        # '다음' 클릭 후 다시 해당 페이지 번호 찾아서 클릭
                                        for sel in pagination_selectors:
                                            try:
                                                page_links = page.locator(f'{sel}:has-text("{page_num}")').all()
                                                for link in page_links:
                                                    if link.is_visible(timeout=1000):
                                                        link.click(timeout=3000)
                                                        print(f"  ✓ 페이지 {page_num} 클릭 성공")
                                                        page_clicked = True
                                                        time.sleep(random.uniform(2, 3))

                                                        # 이 페이지의 리뷰 수집
                                                        self._collect_reviews_from_current_page(page, all_reviews, product_title, brand_name)
                                                        failed_attempts = 0
                                                        break
                                                if page_clicked:
                                                    break
                                            except:
                                                continue
                                        break
                                except:
                                    continue

                            if not next_clicked:
                                print(f"  ✗ '다음' 버튼도 찾을 수 없음")
                                failed_attempts += 1

                        if not page_clicked:
                            print(f"  ✗ 페이지 {page_num}에 접근 실패 (실패 {failed_attempts}/{max_failed_attempts})")
                            failed_attempts += 1

                        page_num += 1

                    if failed_attempts >= max_failed_attempts:
                        print(f"\n[INFO] 연속 {max_failed_attempts}번 실패 - 마지막 페이지로 판단")

                else:
                    # '더보기' 버튼 방식 (페이지네이션이 없을 때만)
                    print("[DEBUG] '더보기' 버튼 확인 중...")

                    more_btn_selectors = [
                        'div#review button:has-text("더보기")',  # 리뷰 영역 내부로 한정
                        'div.productReviewWrap button:has-text("더보기")',
                        'button.review-more:has-text("더보기")',
                    ]

                    more_btn_found = False
                    for selector in more_btn_selectors:
                        try:
                            btn = page.locator(selector).first
                            if btn.is_visible(timeout=2000):
                                more_btn_found = True
                                print(f"  ✓ '더보기' 버튼 발견: {selector}")
                                break
                        except:
                            continue

                    if more_btn_found:
                        print("[INFO] '더보기' 버튼 클릭 시작...")
                        load_more_count = 0
                        max_attempts = 10

                        while load_more_count < max_attempts:
                            clicked = False
                            for selector in more_btn_selectors:
                                try:
                                    btn = page.locator(selector).first
                                    if btn.is_visible(timeout=2000) and btn.is_enabled():
                                        btn.scroll_into_view_if_needed()
                                        btn.click(timeout=3000)
                                        load_more_count += 1
                                        print(f"  ✓ '더보기' 클릭 #{load_more_count}")
                                        time.sleep(random.uniform(2, 3))
                                        clicked = True
                                        break
                                except:
                                    continue

                            if not clicked:
                                print("  ✗ 더 이상 '더보기' 버튼 없음")
                                break
                    else:
                        print("[INFO] 페이지네이션 없음 - 현재 페이지 리뷰만 수집")

                print("\n[INFO] 리뷰 로딩 완료")

                # 브라우저 종료 및 결과 반환
                print(f"\n[SUCCESS] 총 {len(all_reviews)}개의 리뷰 수집 완료")
                browser.close()

        except Exception as e:
            print(f"[FATAL ERROR] 크롤링 중 치명적 오류: {e}")
            import traceback
            traceback.print_exc()
            if browser:
                try:
                    browser.close()
                except:
                    pass
            return {"error": str(e)}

        return {
            "count": len(all_reviews),
            "reviews": all_reviews,
            "product_title": product_title,
            "brand_name": brand_name
        }

    def _collect_reviews_from_current_page(self, page, all_reviews: List[Dict], product_title: Optional[str], brand_name: Optional[str]):
        """현재 페이지의 리뷰를 수집하는 헬퍼 메서드"""
        try:
            # HTML 파싱
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')

            # 리뷰 아이템 찾기
            review_items = []
            item_patterns = [
                ('div', {'data-review-number': True}),
                ('div', {'class': 'reviewList'}),
                ('div', {'class': lambda x: x and any('review' in str(c).lower() and 'item' in str(c).lower() for c in x) if x else False}),
                ('li', {'class': lambda x: x and 'review' in ' '.join(x).lower() if x else False}),
            ]

            for tag, attrs in item_patterns:
                items = soup.find_all(tag, attrs, limit=200)
                if items:
                    review_items = items
                    print(f"  ✓ {len(items)}개의 리뷰 아이템 발견")
                    break

            if not review_items:
                print("  ✗ 이 페이지에서 리뷰를 찾지 못했습니다.")
                return

            # 중복 방지를 위한 review_number 세트
            existing_review_numbers = {r.get('review_number') for r in all_reviews}

            # 각 리뷰 파싱
            page_review_count = 0
            for idx, item in enumerate(review_items, 1):
                try:
                    review_number = item.get('data-review-number', f'unknown_{idx}')

                    # 중복 체크
                    if review_number in existing_review_numbers:
                        continue

                    # 리뷰 내용
                    content_selectors = [
                        'div.reviewContent',
                        'div[class*="reviewContent"]',
                        '.review-content',
                        'p.content',
                    ]
                    content = None
                    for sel in content_selectors:
                        elem = item.select_one(sel)
                        if elem:
                            content = elem.get_text('\n', strip=True)
                            break

                    if not content:
                        content = item.get_text('\n', strip=True)

                    if not content or len(content) < 10:
                        continue

                    # 불필요한 텍스트 제거
                    content = self._clean_review_content(content)

                    # 작성자
                    user_selectors = ['span.userName', 'div[class*="userName"]', '.reviewer', 'span.name']
                    user_id = "익명"
                    for sel in user_selectors:
                        elem = item.select_one(sel)
                        if elem:
                            user_id = elem.get_text(strip=True)
                            break

                    # 평점
                    rating_selectors = ['span.rating', 'div[class*="rating"]', '.rating', '.star']
                    rating = 5.0
                    for sel in rating_selectors:
                        elem = item.select_one(sel)
                        if elem:
                            text = elem.get_text(strip=True)
                            import re
                            match = re.search(r'(\d+(?:\.\d+)?)', text)
                            if match:
                                rating = float(match.group(1))
                                if rating > 5:
                                    rating = 5.0
                            else:
                                star_count = text.count('★')
                                if star_count > 0:
                                    rating = float(star_count)
                            break

                    # 날짜
                    date_selectors = ['span.date', 'div[class*="date"]', '.date', 'time']
                    date_text = ""
                    for sel in date_selectors:
                        elem = item.select_one(sel)
                        if elem:
                            date_text = elem.get_text(strip=True)
                            break

                    # 옵션
                    option_selectors = ['div.option', 'span[class*="option"]', '.option']
                    option = None
                    for sel in option_selectors:
                        elem = item.select_one(sel)
                        if elem:
                            option = elem.get_text(strip=True)
                            break

                    all_reviews.append({
                        "product_title": product_title,
                        "brand_name": brand_name,
                        "user_id": user_id,
                        "rating": rating,
                        "option": option,
                        "content": content[:1000],
                        "date": date_text,
                        "review_number": review_number
                    })
                    page_review_count += 1

                except Exception as e:
                    continue

            print(f"  ✓ 이 페이지에서 {page_review_count}개 리뷰 수집 (중복 제외)")

        except Exception as e:
            print(f"  ✗ 페이지 수집 중 오류: {e}")

    def _clean_review_content(self, content: str) -> str:
        """리뷰 내용에서 불필요한 텍스트 제거"""
        import re

        # 제거할 패턴들
        patterns_to_remove = [
            r'유\s*저\s*썸네일\s*이미지',
            r'신고',
            r'평점\s*\d+',
            r'판매자\s*[:：]\s*[\w가-힣]+',
            r'도움돼요\s*\d+',
            r'댓글\s*\d+',
        ]

        cleaned = content
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        # 연속된 공백/줄바꿈 정리
        cleaned = re.sub(r'\n\s*\n+', '\n', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)

        return cleaned.strip()
