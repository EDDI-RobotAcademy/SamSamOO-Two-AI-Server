from fastapi import APIRouter
from samsam_naver.application.naver_service import search_products, get_reviews

router = APIRouter()

# 🔎 네이버 상품 검색 API
@router.get("/search")
async def search(query: str):
    items = await search_products(query)
    return {"items": items}

# ⭐ 네이버 리뷰 API
@router.get("/products/{catalog_id}/reviews")
async def reviews(catalog_id: str):
    try:
        review_list = await get_reviews(catalog_id)
        return {"reviews": review_list}
    except Exception as e:
        return {"error": str(e)}
