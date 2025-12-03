from pydantic import BaseModel

class Review(BaseModel):
    id: str
    product_id: str
    product_name: str
    rating: float
    text: str
