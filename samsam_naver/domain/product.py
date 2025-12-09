from pydantic import BaseModel

class Product(BaseModel):
    productId: str
    name: str
    price: int
    mall: str | None = None
    image: str | None = None
