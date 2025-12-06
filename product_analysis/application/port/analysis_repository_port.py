from abc import ABC, abstractmethod
from typing import Optional
from product_analysis.domain.entity.analysis_result import AnalysisResult

class AnalysisRepositoryPort(ABC):
    @abstractmethod
    def save(self, result: AnalysisResult) -> AnalysisResult: ...
    @abstractmethod
    def find_latest_by_product_id(self, product_id: int) -> Optional[AnalysisResult]: ...
