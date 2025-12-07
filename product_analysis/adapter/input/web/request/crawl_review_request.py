from pydantic import BaseModel

class ReviewRequest(BaseModel):
    product_name: str
