from fastapi import APIRouter, Depends, HTTPException
from typing import List

from product_analysis.adapter.input.web.request.create_product_analysis_request import CreateProductAnalysisRequest, Provider
from product_analysis.adapter.input.web.response.product_response import ProductResponse
from product_analysis.adapter.input.web.response.analysis_response import AnalysisResponse

from product_analysis.application.usecase.collect_product_usecase import CollectProductUseCase
from product_analysis.application.usecase.analyze_product_usecase import AnalyzeProductUseCase
from product_analysis.application.usecase.get_analysis_result_usecase import GetAnalysisResultUseCase

from product_analysis.infrastructure.repository.product_repository_impl import InMemoryProductRepository
from product_analysis.infrastructure.repository.review_repository_impl import InMemoryReviewRepository
from product_analysis.infrastructure.repository.analysis_repository_impl import InMemoryAnalysisRepository
from product_analysis.infrastructure.external.gmarket_scraper import GmarketScraper
from product_analysis.domain.service.sentiment_analyzer import SentimentAnalyzer

# --- 간단 DI 컨테이너(메모리) ---
_product_repo = InMemoryProductRepository()
_review_repo = InMemoryReviewRepository()
_analysis_repo = InMemoryAnalysisRepository()
_gmarket_scraper = GmarketScraper()

_analyzer = SentimentAnalyzer()   # ✅ 도메인 서비스 인스턴스
# ✅ provider별 UseCase 생성 함수
def _collect_uc(provider: str) -> CollectProductUseCase:
    if provider == "gmarket":
        return CollectProductUseCase(
            scraper=_gmarket_scraper,
            product_repo=_product_repo,
            review_repo=_review_repo,
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def _analyze_uc() -> AnalyzeProductUseCase:
    return AnalyzeProductUseCase(_review_repo, _analysis_repo, _analyzer)

def get_collect_uc(req: CreateProductAnalysisRequest) -> CollectProductUseCase:
    if req.provider == Provider.gmarket:
        scraper = GmarketScraper()
    else:
        raise HTTPException(status_code=400, detail="지원하지 않는 provider")
    return CollectProductUseCase(scraper, _product_repo, _review_repo)

def get_analyze_uc() -> AnalyzeProductUseCase:
    return AnalyzeProductUseCase(_review_repo, _analysis_repo, _analyzer)

def get_get_result_uc() -> GetAnalysisResultUseCase:
    return GetAnalysisResultUseCase(_analysis_repo)

# --- Router ---
router = APIRouter(tags=["product-analysis"])

@router.post("/products/search", response_model=List[ProductResponse])
def search_and_collect(req: CreateProductAnalysisRequest):
    uc = get_collect_uc(req)
    products = uc.execute(
        keyword=req.keyword,
        limit_products=req.limit_products,
        limit_reviews=req.limit_reviews,
    )
    return [ProductResponse(**p.__dict__) for p in products]

@router.post("/search", response_model=List[ProductResponse])
def search_and_collect(req: CreateProductAnalysisRequest):
    print(f"[API] /products/search body={req.dict()}")
    uc = _collect_uc(req.provider)  # 여기서도 provider 로그 찍히면 좋음
    products = uc.execute(req.keyword, req.limit_products, req.limit_reviews)
    print(f"[API] /products/search -> {len(products)} items")
    return [ProductResponse(**p.__dict__) for p in products]

@router.post("/analyses/{product_id}", response_model=AnalysisResponse)
def analyze(product_id: int):
    uc = get_analyze_uc()
    result = uc.execute(product_id)
    return AnalysisResponse(**result.__dict__)

@router.get("/analyses/{product_id}", response_model=AnalysisResponse)
def get_latest_analysis(product_id: int):
    uc = get_get_result_uc()
    result = uc.execute(product_id)
    if not result:
        raise HTTPException(status_code=404, detail="분석 결과가 없습니다.")
    return AnalysisResponse(**result.__dict__)

