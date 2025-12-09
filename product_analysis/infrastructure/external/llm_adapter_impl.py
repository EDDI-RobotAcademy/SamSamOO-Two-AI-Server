import json
from typing import Dict, Any, List
from openai import OpenAI
from product_analysis.application.port.llm_analysis_port import LLMAnalysisPort, LLMAnalysisFailure


class LLMAdapterImpl(LLMAnalysisPort):
    """
    OpenAI API 기반 LLM 분석 어댑터 (할루시네이션 강력 차단 버전)
    - 리뷰 content + rating만 기반으로 분석
    - 제품 카테고리 추측 금지
    - 존재하지 않는 품질 이슈 금지
    - 데이터 생성 요청 금지 (특히 trend, 가상 값)
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        try:
            self._client = OpenAI(api_key=api_key)
            self._model = model
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            self._client = None

    # -----------------------------
    # 내부 LLM 호출 공통 처리
    # -----------------------------
    def _call_llm(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        if not self._client:
            raise LLMAnalysisFailure("LLM client is not initialized.")

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )

            result = json.loads(response.choices[0].message.content)

            if not isinstance(result, dict):
                raise ValueError("LLM returned invalid JSON structure.")

            return result

        except Exception as e:
            print(f"LLM API Call Failed: {e}")
            raise LLMAnalysisFailure(str(e))

    # ================================================================
    # 1단계: 리뷰 기반 Metrics 추출 (트렌드/가상데이터 제거)
    # ================================================================
    def extract_job_metrics(self, review_texts: List[str], product_id: str) -> Dict[str, Any]:

        # 리뷰 50개 샘플링
        reviews_sample = review_texts[:50]

        SYSTEM = (
            "You are a data analysis engine. Your task is to analyze product reviews and output a single JSON object. "
            "출력 형식은 절대로 변경하면 안 된다. aspects는 반드시 dictionary 형태여야 한다. "
            "반드시 아래 JSON 스키마를 준수해라. "
            ""
            "sentiment: { 'positive': number, 'negative': number, 'neutral': number } "
            "aspects: { '<aspect_name>': { 'positive': number, 'negative': number, 'neutral': number }, ... } "
            "keywords: string[] "
            "issues: string[] "
            "trend: { '<week>': number } "
            ""
            "⚠ 절대 aspects를 list로 반환하지 말 것. "
            "⚠ aspects 구조가 dict가 아니면 출력 자체가 잘못된 것이다."
            "모든 출력(JSON 내부 텍스트 포함)은 반드시 한국어로 작성해야 한다."
        )

        USER = f"""
                다음은 상품 {product_id}의 리뷰 데이터입니다.
                
                리뷰 텍스트 {len(review_texts)}개 중 샘플 50개:
                {json.dumps(reviews_sample, ensure_ascii=False)}
                
                리뷰 기반으로 아래 정보를 JSON으로 추출하세요:
                
                - sentiment: 긍정/부정/중립 리뷰 비율 (리뷰 내용으로 판단)
                - aspects: 리뷰에서 자주 언급되는 속성(품질, 사용성, 디자인 등 텍스트 기반으로만 도출)
                - keywords: 리뷰에서 자주 등장하는 단어/표현
                - issues: 리뷰에서 실제로 언급된 불만/부정 요소만
                """

        return self._call_llm(SYSTEM, USER)

    # ================================================================
    # 2단계: 최종 인사이트 요약 (마케팅 + 품질 개선안)
    # ================================================================
    def generate_final_summary(
        self,
        review_texts: List[str],
        metrics_data: Dict[str, Any]
    ) -> Dict[str, Any]:

        SYSTEM = """
                당신은 리뷰 기반 제품 분석 전문가입니다.
                반드시 리뷰 content와 rating + metrics_data만 근거로 분석하세요.
                
                ⚠ 다음은 절대 금지:
                - 리뷰에 없는 품질 문제 생성
                - 제품 카테고리 추측 (전자제품/마스크 등 금지)
                - 기능 추측 (배터리, 화면 등 금지)
                - 리뷰에 없는 부정 이슈 생성
                - 가상 정보 생성 (트렌드, 성능, 기능 등)

                🎯 출력 목표:
                "결과는 반드시 한국어로 작성한다. "
                아래 내용을 포함하는 JSON 한 객체 생성:
                - summary: 리뷰 기반 전체 요약
                - insights:
                    - marketing_insights: 강점/개선 메시지
                    - quality_insights: 실제 리뷰에 기반한 품질 문제 및 개선방안
                - evidence_ids: 분석의 근거가 된 리뷰 인덱스 또는 ID 목록
                - metadata: LLM 버전, 분석 시간 등
                """

        USER = f"""
                다음은 1단계 metrics 데이터입니다:
                {json.dumps(metrics_data, ensure_ascii=False)}
                
                그리고 리뷰 리스트 중 일부입니다:
                {json.dumps(review_texts[:50], ensure_ascii=False)}
                
                위 데이터만을 사용해 요약과 마케팅/품질 인사이트를 생성하세요.
                """

        return self._call_llm(SYSTEM, USER)