import os
import openai
from typing import List
from product_analysis.application.port.llm_service_port import LLMServicePort


class LLMAdapter(LLMServicePort):
    """OpenAI GPT를 통한 개선점 생성"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY 환경변수가 필요합니다.")
        openai.api_key = api_key

    def generate_improvements(self, product_name: str, negative_attrs: List[str]) -> List[str]:
        if not negative_attrs:
            return ["현재 리뷰에서 눈에 띄는 개선점이 없습니다."]

        prompt = f"""
        상품 '{product_name}'의 리뷰에서 다음 속성들이 부정적으로 평가되었습니다: {', '.join(negative_attrs)}.
        판매자가 참고할 수 있는 구체적 개선점 3개를 bullet point 형식으로 작성해주세요.
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        text = response.choices[0].message.content
        return [line.strip("-• \n") for line in text.split("\n") if line.strip()]
