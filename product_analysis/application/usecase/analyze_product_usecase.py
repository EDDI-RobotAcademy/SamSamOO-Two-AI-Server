from datetime import datetime
from typing import Dict
from product_analysis.application.port.review_repository_port import ReviewRepositoryPort
from product_analysis.application.port.analysis_repository_port import AnalysisRepositoryPort
from product_analysis.domain.entity.analysis_result import AnalysisResult
from product_analysis.domain.service.sentiment_analyzer import SentimentAnalyzer

class AnalyzeProductUseCase:
    def __init__(self, review_repo: ReviewRepositoryPort, analysis_repo: AnalysisRepositoryPort,
                 analyzer: SentimentAnalyzer):
        self.review_repo = review_repo
        self.analysis_repo = analysis_repo
        self.analyzer = analyzer

    def execute(self, product_id: int) -> AnalysisResult:
        reviews = self.review_repo.find_by_product_id(product_id, limit=1000)

        pos = neg = neu = 0
        kw: Dict[str, int] = {}
        rating_sum = 0
        rating_cnt = 0

        for rv in reviews:
            r = self.analyzer.analyze_text(rv.content or "")
            # 별점 보정
            blended = self.analyzer.blend_with_rating(r.score, rv.rating)
            if blended > 0: pos += 1
            elif blended < 0: neg += 1
            else: neu += 1

            # 속성 합산
            for k, v in r.attrs.items():
                kw[k] = kw.get(k, 0) + v

            if rv.rating is not None:
                rating_sum += rv.rating
                rating_cnt += 1

        avg_rating = round(rating_sum / rating_cnt, 2) if rating_cnt else None

        result = AnalysisResult(
            id=None,
            product_id=product_id,
            pos_count=pos,
            neg_count=neg,
            neu_count=neu,
            top_keywords=dict(sorted(kw.items(), key=lambda x: x[1], reverse=True)[:10]),
            avg_rating=avg_rating,
            analyzed_at=datetime.now()
        )
        return self.analysis_repo.save(result)
