from typing import List, Optional
from product_analysis.application.port.product_repository_port import ProductRepositoryPort
from product_analysis.domain.entity.product import Product

class InMemoryProductRepository(ProductRepositoryPort):
    def __init__(self):
        self._data: List[Product] = []
        self._seq = 1

    def save(self, product: Product) -> Product:
        product.id = self._seq
        self._seq += 1
        self._data.append(product)
        return product

    def find_by_item_code(self, source: str, item_code: str) -> Optional[Product]:
        return next((p for p in self._data if p.source == source and p.item_code == item_code), None)

    def find_by_id(self, pid: int) -> Optional[Product]:
        return next((p for p in self._data if p.id == pid), None)

    def find_all(self, limit: int = 10) -> List[Product]:
        return self._data[:limit]
