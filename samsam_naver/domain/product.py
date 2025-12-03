from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    id: str
    name: str
    price: int
    mall_name: Optional[str] = None
