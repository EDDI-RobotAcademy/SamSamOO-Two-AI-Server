from typing import List, Optional
from abc import ABC, abstractmethod
from product_analysis.domain.entity.product import Product, Platform


class ProductRepositoryPort(ABC):

    @abstractmethod
    def save(self, product: Product) -> Product:
        pass

    @abstractmethod
    def update(self, product: Product) -> Product:
        pass

    @abstractmethod
    def delete(self, source: Platform, source_product_id: str) -> bool:
        pass

    @abstractmethod
    def find_by_composite_key(self, source: Platform, source_product_id: str) -> Optional[Product]:
        pass

    @abstractmethod
    def find_all(self, limit: int) -> List[Product]:
        pass

    @abstractmethod
    def find_by_title_like(self, source: Platform, keyword: str) -> List[Product]:
        pass
