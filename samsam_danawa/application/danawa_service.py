import asyncio
from samsam_danawa.infrastructure.danawa_scraper import (
    search_danawa_products,
    get_danawa_reviews
)

async def danawa_search_products(query: str):
    results = await asyncio.to_thread(search_danawa_products, query)
    return [p.to_dict() for p in results]

async def danawa_get_reviews(product_id: str):
    reviews = await asyncio.to_thread(get_danawa_reviews, product_id)
    return [r.dict() for r in reviews]
