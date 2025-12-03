from fastapi import APIRouter, Query
from typing import List

from samsam_naver.application.naver_service import NaverService
from samsam_naver.domain.product import Product
from samsam_naver.domain.review import Review

router = APIRouter(prefix="/naver", tags=["Naver"])

@router.get("/products", response_model=List[Product])
def search_products(q: str = Query("노트북")):
    return NaverService.get_products(q)


@router.get("/products/{product_id}/reviews", response_model=List[Review])
def get_reviews(product_id: str, product_name: str):
    product = Product(id=product_id, name=product_name, price=0)
    return NaverService.get_reviews(product)
