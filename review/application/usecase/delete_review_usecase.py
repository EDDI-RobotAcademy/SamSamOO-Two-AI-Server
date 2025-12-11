from typing import Dict
from review.application.port.analysis_result_repository_port import AnalysisResultRepositoryPort
from review.application.port.insight_result_repository_port import InsightResultRepositoryPort
from review.application.port.analysis_job_repository_port import AnalysisJobRepositoryPort
from review.application.port.review_repository_port import ReviewRepositoryPort

class DeleteReviewsUseCase:
    def __init__(
        self,
        analysis_repo: AnalysisResultRepositoryPort,
        insight_repo: InsightResultRepositoryPort,
        job_repo: AnalysisJobRepositoryPort,
        review_repo: ReviewRepositoryPort,
    ):
        self.analysis_repo = analysis_repo
        self.insight_repo = insight_repo
        self.job_repo = job_repo
        self.review_repo = review_repo

    def execute(self, source: str, product_id: str) -> Dict[str, int]:
        deleted_insight  = self.insight_repo.delete_by_product(source, product_id)
        deleted_analysis = self.analysis_repo.delete_by_product(source, product_id)
        deleted_jobs     = self.job_repo.delete_by_product(source, product_id)
        deleted_reviews  = self.review_repo.delete_by_product(source, product_id)
        return {
            "insight": deleted_insight,
            "analysis": deleted_analysis,
            "jobs": deleted_jobs,
            "reviews": deleted_reviews,
        }
