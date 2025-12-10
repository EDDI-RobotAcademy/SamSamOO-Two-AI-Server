from typing import Optional
from datetime import datetime

class Account:
    def __init__(self, email: str, nickname: str):
        self.id: Optional[int] = None
        self.email = email
        self.nickname = nickname
        self.created_at: datetime = datetime.utcnow()
        self.updated_at: datetime = datetime.utcnow()

        self.terms_agreed: bool = False
        self.terms_agreed_at: Optional[datetime] = None

    def update_nickname(self, nickname: str):
        self.nickname = nickname
        self.updated_at = datetime.utcnow()

    # ✅ 약관 동의 처리 함수 추가
    def agree_terms(self):
        self.terms_agreed = True
        self.terms_agreed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
