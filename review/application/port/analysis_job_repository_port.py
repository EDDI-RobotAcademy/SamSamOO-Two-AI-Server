from abc import ABC, abstractmethod

class AnalysisJobRepositoryPort(ABC):
    @abstractmethod
    def delete_by_product(self, source: str, product_id: str) -> int:
        ...
