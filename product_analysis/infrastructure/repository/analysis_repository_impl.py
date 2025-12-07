from typing import Optional, List
from product_analysis.application.port.analysis_repository_port import AnalysisRepositoryPort
from product_analysis.domain.entity.analysis_result import AnalysisResult

class InMemoryAnalysisRepository(AnalysisRepositoryPort):
    def __init__(self):
        self._data: List[AnalysisResult] = []
        self._seq = 1

    def save(self, result: AnalysisResult) -> AnalysisResult:
        result.id = self._seq
        self._seq += 1
        self._data.append(result)
        return result

    def find_latest_by_product_id(self, product_id: int) -> Optional[AnalysisResult]:
        rows = [r for r in self._data if r.product_id == product_id]
        return rows[-1] if rows else None
