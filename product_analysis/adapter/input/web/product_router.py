from fastapi import APIRouter, HTTPException, Query
from typing import List

# --- Domain & Application Imports ---
from product_analysis.domain.entity.product import Product, Platform
from product_analysis.application.usecase.product_usecase import ProductUseCase
from product_analysis.domain.service import analyzer_service
from product_analysis.domain.service.sentiment_analyzer import SentimentAnalyzer
from product_analysis.infrastructure.external.llm_adapter import LLMAdapter
from product_analysis.infrastructure.repository.product_repository_impl import ProductRepositoryImpl
from product_analysis.adapter.input.web.request.create_product_request import ProductCreateRequest
from product_analysis.adapter.input.web.response.product_response import ProductResponse

# 임시추가 리펙터링 및 도메인 분리 필요
from product_analysis.adapter.input.web.request.crawl_review_request import ReviewRequest
from config.database.session import get_db_session
from product_analysis.infrastructure.orm.product_orm import ProductORM
from product_analysis.infrastructure.external.elevenSt_scraper import ElevenStScraperAdapter
from fastapi.concurrency import run_in_threadpool

# ⭐️ 의존성 주입을 위한 임시 설정 (실제 프로젝트에서는 Depends 사용 권장)
_product_repo = ProductRepositoryImpl()
product_uc = ProductUseCase(_product_repo)

# ----------------------------------------------------------
product_router = APIRouter(tags=["product"])


# ----------------------------------------------------------------------
# 1. 상품 생성 (UC-1 반영: source_product_id 전달 수정)
# ----------------------------------------------------------------------
@product_router.post("/create", response_model=ProductResponse)
def create_product(req: ProductCreateRequest):
    """새 상품 정보를 저장합니다. (Full Path: /products/create)"""

    # 🚨 seller_id는 인증 시스템에서 가져와야 하지만, 임시로 1을 사용합니다.
    SELLER_ID = 1

    # ⭐️ 수정: source_product_id를 Product.create에 올바르게 전달 ⭐️
    new_product = Product.create(
        source=req.source,
        source_product_id=req.source_product_id,  # ⭐️ DTO에서 받은 복합 키 전달
        title=req.title,
        source_url=req.source_url,  # DTO의 url을 source_url로 전달
        price=req.price,
        seller_id=SELLER_ID,  # ⭐️ 판매자 ID 전달
    )

    try:
        saved_product = product_uc.create_product(new_product)
        return ProductResponse(**saved_product.__dict__)
    except Exception as e:
        # 중복 등록 또는 DB 오류 처리
        raise HTTPException(status_code=400, detail=str(e))


# ----------------------------------------------------------------------
# 2. 상품 단건 조회 (복합 키 기반으로 변경)
# ----------------------------------------------------------------------
@product_router.get("/read", response_model=ProductResponse)
def get_product_by_composite_key(
        source: Platform = Query(..., description="플랫폼 출처"),
        source_product_id: str = Query(..., description="원본 상품 ID")
):
    """source와 source_product_id 복합 키로 상품을 조회합니다. (Full Path: /products/read?source=...&source_product_id=...)"""

    product = product_uc.get_product_by_composite_key(source, source_product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductResponse(**product.__dict__)


# ----------------------------------------------------------------------
# 3. 상품 전체 목록 조회 (기존 유지)
# ----------------------------------------------------------------------
@product_router.get("/list", response_model=List[ProductResponse])
def get_all_products(limit: int = Query(10, ge=1)):
    """상품 목록을 조회합니다. (Full Path: /products/list)"""
    products = product_uc.get_all_products(limit)
    return [ProductResponse(**p.__dict__) for p in products]


# ----------------------------------------------------------------------
# 4. 상품 검색 (기존 유지)
# ----------------------------------------------------------------------
@product_router.get("/search", response_model=List[ProductResponse])
def search_products_by_title(
        source: Platform = Query(...),
        keyword: str = Query(...)
):
    """제목에 키워드가 포함된 상품 목록을 조회합니다. (Full Path: /products/search)"""
    products = product_uc.search_products(source, keyword)
    return [ProductResponse(**p.__dict__) for p in products]


# ----------------------------------------------------------------------
# 6. 상품 정보 업데이트 (Read-Modify-Write 패턴 적용)
# ----------------------------------------------------------------------
@product_router.put("/update", response_model=ProductResponse)
def update_product(req: ProductCreateRequest):
    """상품 정보를 수정합니다. (Full Path: /products/update)"""

    existing_product = product_uc.get_product_by_composite_key(req.source, req.source_product_id)

    if not existing_product:
        raise HTTPException(status_code=404, detail="업데이트할 상품이 존재하지 않습니다.")

    existing_product.title = req.title
    existing_product.source_url = req.source_url
    existing_product.price = req.price

    try:
        updated_product = product_uc.update_product(existing_product)
        return ProductResponse(**updated_product.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="상품 업데이트 실패: " + str(e))


# ----------------------------------------------------------------------
# 7. 상품 삭제 (ProductUseCase.delete_product)
# ----------------------------------------------------------------------
@product_router.delete("/delete", status_code=204)
def delete_product(
        source: Platform = Query(..., description="플랫폼 출처"),
        source_product_id: str = Query(..., description="원본 상품 ID")
):
    """복합 키를 사용하여 상품을 삭제합니다. (Full Path: /products/delete?source=...&source_product_id=...)"""

    if not product_uc.delete_product(source, source_product_id):
        raise HTTPException(status_code=404, detail="삭제할 상품이 DB에 존재하지 않습니다.")

    # HTTP 204 No Content는 삭제 성공 시 본문 없이 응답하는 표준입니다.
    return

# 임시 추가: 상품명 → 상품코드 조회 + 리뷰 크롤링 API
# ======================================================================


def get_product_code_by_name(product_name: str) -> str | None:
    db = get_db_session()
    try:
        product = db.query(ProductORM).filter(ProductORM.title == product_name).first()
        return product.source_product_id if product else None
    finally:
        db.close()


@product_router.post("/reviews/get")
async def get_reviews(req: ReviewRequest):
    product_code = get_product_code_by_name(req.product_name)
    if not product_code:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    # 동기 크롤러를 threadpool에서 실행
    result = await run_in_threadpool(ElevenStScraperAdapter.crawl_11st_reviews, int(product_code))

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result

@product_router.post("/reviews/analyze")
async def analyze_reviews(req: ReviewRequest):
    # 1️⃣ DB에서 상품 코드 조회
    product_code = get_product_code_by_name(req.product_name)
    if not product_code:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    # 2️⃣ 리뷰 크롤링
    reviews_result = await run_in_threadpool(ElevenStScraperAdapter.crawl_11st_reviews, int(product_code))
    if "error" in reviews_result:
        raise HTTPException(status_code=500, detail=reviews_result["error"])

    review_texts = [r["content"] for r in reviews_result["reviews"]]

    # 3️⃣ SentimentAnalyzer로 속성별 점수 계산
    senti = SentimentAnalyzer()
    attr_summary = {}
    for text in review_texts:
        attrs, score = senti.analyze_text(text)
        for k, v in attrs.items():
            attr_summary[k] = attr_summary.get(k, 0) + (v if score >= 0 else -v)

    negative_attrs = [k for k, v in attr_summary.items() if v < 0]

    # 4️⃣ LLM 호출 → 개선점 생성
    llm = LLMAdapter()
    improvements = llm.generate_improvements(req.product_name, negative_attrs)

    return {
        "product_name": req.product_name,
        "reviews_count": len(reviews_result["reviews"]),
        "negative_attrs": negative_attrs,
        "improvements": improvements
    }
