from product_analysis.application.port.analysis_repository_port import AnalysisRepositoryPort
from product_analysis.domain.entity.analysis_result import AnalysisResult

class GetAnalysisResultUseCase:
    def __init__(self, analysis_repo: AnalysisRepositoryPort):
        self.analysis_repo = analysis_repo

    def execute(self, product_id: int) -> AnalysisResult | None:
        return self.analysis_repo.find_latest_by_product_id(product_id)
