from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from typing import Optional, TypedDict

class ProductRow(TypedDict, total=False):
    source: str
    source_product_id: str
    analysis_status: str
    review_count: int

class ProductRepositoryPort(ABC):
    @abstractmethod
    def get(self, source: str, product_id: str) -> Optional[Dict[str, Any]]:
        """DB Row or DTO 반환(analysis_status 포함)"""
        ...

    @abstractmethod
    def update_status(
        self,
        source: str,
        product_id: str,
        status: str,
        review_count: int = 0,
    ) -> None:
        ...
