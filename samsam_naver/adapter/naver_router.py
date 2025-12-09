from fastapi import APIRouter, Query
from samsam_naver.application.naver_service import NaverService

router = APIRouter()

@router.get("/search")
async def search_products_route(query: str = Query(...)):
    items = await NaverService.search_products(query)
    return {"items": items}

@router.get("/reviews")
async def get_reviews_route(catalogId: str = Query(...)):
    reviews = await NaverService.get_reviews(catalogId)
    return {"reviews": reviews}
