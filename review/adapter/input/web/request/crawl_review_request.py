from pydantic import BaseModel

class ReviewRequest(BaseModel):
    product_name: str

class FetchReviewsRequest(BaseModel):
    platform: str
    product_id: str