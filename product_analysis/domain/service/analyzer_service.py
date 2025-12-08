from product_analysis.domain.service.sentiment_analyzer import SentimentAnalyzer
from product_analysis.infrastructure.external.elevenSt_scraper import ElevenStScraperAdapter
from product_analysis.infrastructure.external.llm_adapter import LLMAdapter


class ProductRepository:
    pass


class ReviewAnalyzer:
    def __init__(self, product_repo: ProductRepository, llm_adapter: LLMAdapter):
        self.product_repo = product_repo
        self.llm_adapter = llm_adapter
        self.senti = SentimentAnalyzer()

    def analyze_reviews(self, product_name: str):
        product_code = self.product_repo.get_product_code_by_name(product_name)
        if not product_code:
            return {"error": "상품을 찾을 수 없습니다."}

        reviews = ElevenStScraperAdapter.crawl_11st_reviews(int(product_code))
        if "error" in reviews:
            return {"error": reviews["error"]}

        attr_summary = {}
        for r in reviews["reviews"]:
            sr = self.senti.analyze_text(r["content"])
            score = self.senti.blend_with_rating(sr.score, r.get("rating"))
            for k, v in sr.attrs.items():
                attr_summary[k] = attr_summary.get(k, 0) + (v * (1 if score > 0 else -1))

        negative_attrs = [k for k, v in attr_summary.items() if v < 0]
        improvements = self.llm_adapter.generate_improvements(product_name, negative_attrs)

        return {
            "product_name": product_name,
            "reviews_count": len(reviews["reviews"]),
            "improvements": improvements,
        }
