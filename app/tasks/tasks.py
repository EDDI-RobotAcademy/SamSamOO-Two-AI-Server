import os
from datetime import datetime, timedelta
# 아래 두줄 절대 삭제 금지
import product.infrastructure.orm.product_orm
import review.infrastructure.orm.review_orm

from celery_app import celery_app
from config.database.session import get_db_session

# Review 도메인 import
from product.domain.entity.product import Product
from review.application.usecase.fetch_review_usecase import FetchReviewsUseCase
from review.infrastructure.repository.review_repository_impl import ReviewRepositoryImpl
from review.application.port.scraper_factory import get_scraper_adapter  # 팩토리 함수

# Product Analysis 도메인 import
from product_analysis.application.usecase.analyze_product_usecase import ProductAnalysisUsecase
from product_analysis.infrastructure.repository.analysis_repository_impl import ReviewAnalysisRepositoryImpl
from product_analysis.domain.service.analyzer_service import ReviewAnalysisService
from product_analysis.infrastructure.external.llm_adapter_impl import LLMAdapterImpl
from product.infrastructure.repository.product_repository_task_impl import ProductRepositoryTaskImpl

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "YOUR_FALLBACK_KEY")


@celery_app.task(bind=True, name="review.start_crawl")
def start_review_crawl_task(self, platform: str, source_product_id: str):
    """[순서 1] 리뷰를 크롤링하고 'Review' 테이블에 저장합니다."""

    session = get_db_session()
    product_repo = ProductRepositoryTaskImpl(session=session)

    try:
        # ===== 🔥 중복 실행 방지 🔥 =====
        from product.infrastructure.orm.product_orm import ProductORM

        product = session.query(ProductORM).filter(
            ProductORM.source == platform,
            ProductORM.source_product_id == source_product_id
        ).first()

        if not product:
            print(f"[ERROR] 상품을 찾을 수 없습니다: {platform}/{source_product_id}")
            return {"error": "Product not found"}

        current_status = product.analysis_status

        # PENDING이나 FAILED가 아니면 즉시 종료
        if current_status not in ["PENDING", "FAILED"]:
            print(f"[SKIP] 이미 처리 중/완료된 상품")
            print(f"  - 상품: {platform}/{source_product_id}")
            print(f"  - 현재 상태: {current_status}")
            print(f"  - Task ID: {self.request.id}")
            return {
                "skipped": True,
                "reason": f"Already in status: {current_status}",
                "source_product_id": source_product_id,
                "platform": platform
            }

        print(f"[START] 크롤링 시작: {platform}/{source_product_id}")
        # ===== 중복 실행 방지 끝 =====

        _review_repo = ReviewRepositoryImpl(session=session)
        _scraper_adapter = get_scraper_adapter(platform)

        # 상태: CRAWLING (락 역할)
        product_repo.update_analysis_status(
            source=platform,
            source_product_id=source_product_id,
            status="CRAWLING",
        )
        session.commit()

        review_uc = FetchReviewsUseCase(_scraper_adapter, _review_repo)
        product = Product.create_for_crawl_request(platform=platform, product_id=source_product_id)

        reviews = review_uc.execute(product)  # 크롤링 실행

        if reviews:
            print(f"[SAVE] {len(reviews)}개 리뷰 저장 시작")

            # FetchReviewsUseCase 에서 진행되던거 옿김.
            _review_repo.save_all(
                reviews,
                source=platform,
                source_product_id=source_product_id
            )

            # 제품 상태 추가
            product_repo.update_analysis_status(
                source=platform,
                source_product_id=source_product_id,
                status="COLLECTED"
            )
            # Task가 커밋 책임
            session.commit()

            print(f"[SUCCESS] 크롤링 완료: {len(reviews)}개 저장")
        else:
            print(f"[WARNING] 수집된 리뷰 없음")

        # 다음 Task로 전달할 데이터 반환
        return {"source_product_id": source_product_id, "platform": platform}

    except Exception as e:
        print(f"[ERROR] 크롤링 실패: {e}")
        try:
            product_repo.update_analysis_status(
                source=platform,
                source_product_id=source_product_id,
                status="FAILED",
            )
            session.commit()
        except:
            pass

        session.rollback()
        # 재시도 로직
        raise self.retry(exc=e, countdown=30, max_retries=3)
    finally:
        session.close()


@celery_app.task(bind=True, name="analysis.start")
def start_review_analysis_task(self, previous_result: dict):
    """[순서 2] 크롤링된 리뷰를 분석하고 'Review Analysis' 테이블에 저장합니다."""

    source_product_id = previous_result.get("source_product_id")
    source = previous_result.get("platform")

    session = get_db_session()
    product_repo = ProductRepositoryTaskImpl(session=session)

    try:
        # ===== 🔥 중복 실행 방지 🔥 =====
        from product.infrastructure.orm.product_orm import ProductORM

        product = session.query(ProductORM).filter(
            ProductORM.source == source,
            ProductORM.source_product_id == source_product_id
        ).first()

        if not product:
            print(f"[ERROR] 상품을 찾을 수 없습니다: {source}/{source_product_id}")
            return {"error": "Product not found"}

        current_status = product.analysis_status

        # COLLECTED가 아니면 즉시 종료
        if current_status != "COLLECTED":
            print(f"[SKIP] 분석 불가 상태")
            print(f"  - 상품: {source}/{source_product_id}")
            print(f"  - 현재 상태: {current_status}")
            print(f"  - Task ID: {self.request.id}")
            return {
                "skipped": True,
                "reason": f"Cannot analyze in status: {current_status}",
                "source_product_id": source_product_id,
                "platform": source
            }

        print(f"[START] 분석 시작: {source}/{source_product_id}")
        # ===== 중복 실행 방지 끝 =====

        # 상태 업데이트: ANALYZING
        product_repo.update_analysis_status(
            source=source,
            source_product_id=source_product_id,
            status="ANALYZING"
        )
        session.commit()

        # Product Analysis UseCase에 필요한 의존성 초기화
        analysis_repo = ReviewAnalysisRepositoryImpl(session=session)
        llm = LLMAdapterImpl(api_key=OPENAI_API_KEY)
        analysis_service = ReviewAnalysisService(llm_port=llm, analysis_repo=analysis_repo)
        analysis_uc = ProductAnalysisUsecase(analysis_service)

        # 분석 실행
        analysis_uc.execute(source=source, source_product_id=source_product_id)

        # 상태 업데이트: ANALYZED
        product_repo.update_analysis_status(
            source=source,
            source_product_id=source_product_id,
            status="ANALYZED"
        )

        session.commit()

        print(f"[SUCCESS] 분석 완료")

        return {"status": "Analysis Completed"}

    except Exception as e:
        print(f"[ERROR] 분석 실패: {e}")
        try:
            product_repo.update_analysis_status(
                source=source,
                source_product_id=source_product_id,
                status="FAILED"
            )
            session.commit()
        except:
            pass
        session.rollback()
        # 재시도 로직
        raise self.retry(exc=e, countdown=60, max_retries=3)
    finally:
        session.close()