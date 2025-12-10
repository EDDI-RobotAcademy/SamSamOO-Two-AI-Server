from typing import Dict, Any, List


class JobMetrics:
    def __init__(self, total_reviews: int, sentiment: Dict[str, Any], aspects: Dict[str, Any],
                 keywords: List[str], issues: List[str], trend: Dict[str, Any]):
        self.total_reviews = total_reviews
        self.sentiment = sentiment
        self.aspects = aspects
        self.keywords = keywords
        self.issues = issues
        self.trend = trend

    @classmethod
    def from_llm_data(cls, metrics_raw_data: Dict[str, Any], total_reviews: int):
        """LLM 원시 데이터를 엔티티로 변환하는 팩토리 메서드."""
        # LLMAdapterImpl이 반환하는 JSON 키를 매핑합니다.
        return cls(
            total_reviews=total_reviews,
            sentiment=metrics_raw_data.get('sentiment', {}),
            aspects=metrics_raw_data.get('aspects', {}),
            keywords=metrics_raw_data.get('keywords', []),
            issues=metrics_raw_data.get('issues', []),
            trend=metrics_raw_data.get('trend', {})
        )

    def to_db_dict(self):
        # DB 저장을 위해 JSON 필드를 매핑
        return {
            "total_reviews": self.total_reviews,
            "sentiment_json": self.sentiment,
            "aspects_json": self.aspects,
            "keywords_json": self.keywords,
            "issues_json": self.issues,
            "trend_json": self.trend
        }