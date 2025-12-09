from product_analysis.domain.service.analyzer_service import ReviewAnalysisService

from typing import Dict, Any

class ProductAnalysisUsecase:
    """
    상품 분석 요청을 처리하는 애플리케이션의 사용 사례 (Usecase).
    """
    def __init__(self, analysis_service: ReviewAnalysisService):
        # 도메인 서비스를 주입받습니다.
        self._analysis_service = analysis_service

    def execute(self, source: str, source_product_id: str) -> Dict[str, Any]:
        """
        라우터에서 호출되는 주요 메서드.
        실제 비즈니스 로직 실행을 도메인 서비스에 위임합니다.
        """
        # Job 실행을 도메인 서비스에 위임
        return self._analysis_service.analyze_product_reviews(
            source=source,
            source_product_id=source_product_id
        )