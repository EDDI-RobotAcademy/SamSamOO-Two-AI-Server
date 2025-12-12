from pydantic import BaseModel

class ReviewAnalyzeRequest(BaseModel):
    platform: str
    product_id: str
