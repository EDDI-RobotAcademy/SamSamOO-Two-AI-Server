from fastapi import APIRouter
from samsam_danawa.application.danawa_service import (
    danawa_search_products,
    danawa_get_reviews
)

router = APIRouter()

# 🔎 다나와 상품 검색
@router.get("/search")
async def search(query: str):
    items = await danawa_search_products(query)
    return {"items": items}


# ⭐ 다나와 상품 리뷰
@router.get("/products/{product_id}/reviews")
async def reviews(product_id: str):
    try:
        review_list = await danawa_get_reviews(product_id)
        return {"reviews": review_list}
    except Exception as e:
        return {"error": str(e)}
