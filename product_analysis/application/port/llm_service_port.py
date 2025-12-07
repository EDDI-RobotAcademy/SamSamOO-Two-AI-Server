from typing import List

class LLMServicePort:
    def generate_improvements(self, product_name: str, negative_attrs: List[str]) -> List[str]:
        raise NotImplementedError
