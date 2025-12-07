from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class SentimentResult:
    score: int          # 전체 점수(강조/부정어 반영)
    label: str          # "POS" | "NEG" | "NEU"
    attrs: Dict[str, int]  # 속성 키워드 카운트

class SentimentAnalyzer:
    """
    외부 의존 없는 순수 룰 기반 감정/속성 분석기.
    - 간단 한국어 포함 여부 기반 (형태소 분석기 없이도 동작)
    - 강조어/부정어 처리
    """
    POS = {"좋", "만족", "추천", "훌륭", "빠르", "예쁘", "튼튼", "가성비", "저렴", "정확"}
    NEG = {"별로", "실망", "불만", "느리", "파손", "불량", "최악", "비쌈", "아쉬움", "오류", "지연"}

    # 강조/완화/부정어(간단 규칙)
    INTENSIFIERS = {"매우": 2, "정말": 2, "진짜": 2, "너무": 2, "아주": 2}
    DOWNTONERS   = {"그냥": -1, "살짝": -1, "조금": -1}
    NEGATORS     = {"아니", "안 ", "않", "못 ", "무슨 ", "전혀"}

    # 속성 카테고리 사전 (원하면 .yaml로 뺄 수 있음)
    ATTRS = {
        "배송": {"배송", "빠르", "느리", "지연", "포장", "택배", "송장"},
        "품질": {"품질", "재질", "내구", "하자", "마감", "튼튼", "불량"},
        "가성비": {"가성비", "가격", "할인", "저렴", "비쌈"},
        "AS": {"교환", "환불", "AS", "고객센터", "응대"},
        "사이즈": {"사이즈", "크다", "작다", "핏", "옵션", "색상", "색깔"},
        "기타": {"냄새", "소음", "발송", "정품", "위생"},
    }

    def analyze_text(self, text: str) -> SentimentResult:
        t = (text or "").strip()
        if not t:
            return SentimentResult(0, "NEU", {})

        base = 0
        # 긍/부 단어 점수
        pos_hits = sum(1 for w in self.POS if w in t)
        neg_hits = sum(1 for w in self.NEG if w in t)
        base += pos_hits
        base -= neg_hits

        # 강조/완화 가중
        for w, wv in self.INTENSIFIERS.items():
            if w in t: base += wv
        for w, wv in self.DOWNTONERS.items():
            if w in t: base += wv  # 완화는 -1 값

        # 부정어가 문장에 있으면 극성 뒤집기(아주 단순화)
        if base != 0 and any(ng in t for ng in self.NEGATORS):
            base = -base

        # 속성 카운트
        attr_counts: Dict[str, int] = {}
        for cat, words in self.ATTRS.items():
            c = sum(1 for w in words if w in t)
            if c > 0:
                attr_counts[cat] = c

        label = "NEU"
        if base > 0: label = "POS"
        elif base < 0: label = "NEG"

        return SentimentResult(score=base, label=label, attrs=attr_counts)

    def blend_with_rating(self, senti_score: int, rating: int | None) -> int:
        """
        별점이 있으면 소프트 가중치(텍스트 0.7, 별점 0.3)로 보정한 정수 극성 반환
        rating 1~5 기준: 1,2=부정(-1), 3=중립(0), 4,5=긍정(+1)
        """
        if rating is None:
            return senti_score
        rpol = -1 if rating <= 2 else (0 if rating == 3 else 1)
        val = round(0.7 * senti_score + 0.3 * rpol)
        return int(val)
