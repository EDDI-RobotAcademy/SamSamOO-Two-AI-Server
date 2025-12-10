import os
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

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "YOUR_FALLBACK_KEY")


@celery_app.task(bind=True, name="review.start_crawl")
def start_review_crawl_task(self, platform: str, source_product_id: str):
    """[순서 1] 리뷰를 크롤링하고 'Review' 테이블에 저장합니다."""

    session = get_db_session()

    try:
        # 1. Review UseCase에 필요한 의존성 초기화
        _review_repo = ReviewRepositoryImpl(session=session)
        _scraper_adapter = get_scraper_adapter(platform)

        review_uc = FetchReviewsUseCase(_scraper_adapter, _review_repo)
        product = Product.create_for_crawl_request(platform=platform, product_id=source_product_id)

        reviews = review_uc.execute(product)  # 크롤링 실행

        if reviews:
            # 4-2. save_all 호출 시 인자 모두 전달
            _review_repo.save_all(
                reviews,
                source=platform,
                source_product_id=source_product_id
            )
            # 4-3. Task가 커밋 책임
            session.commit()
        # 3. 다음 Task로 전달할 데이터 반환
        return {"source_product_id": source_product_id, "platform": platform}

    except Exception as e:
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

    try:
        # 1. Product Analysis UseCase에 필요한 의존성 초기화
        analysis_repo = ReviewAnalysisRepositoryImpl(session=session)
        llm = LLMAdapterImpl(api_key=OPENAI_API_KEY)
        analysis_service = ReviewAnalysisService(llm_port=llm, analysis_repo=analysis_repo)
        analysis_uc = ProductAnalysisUsecase(analysis_service)

        # 2. 분석 실행 (이 UseCase 내부에 DB 저장 로직이 포함되어야 합니다.)
        analysis_uc.execute(source=source, source_product_id=source_product_id)

        session.commit()  # 분석 결과 저장 후 커밋

        return {"status": "Analysis Completed"}

    except Exception as e:
        session.rollback()
        # 재시도 로직
        raise self.retry(exc=e, countdown=60, max_retries=3)
    finally:
        session.close()