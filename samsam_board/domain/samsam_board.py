from typing import Optional
from datetime import datetime

class SamsamBoard:
    def __init__(
        self,
        title: str,
        content: str,
        writer_nickname: Optional[str] = None,
    ):
        self.id: Optional[int] = None
        self.title = title
        self.content = content
        self.writer_nickname = writer_nickname
        self.created_at: datetime = datetime.utcnow()
        self.updated_at: datetime = datetime.utcnow()

    def update(self, title: str, content: str):
        self.title = title
        self.content = content
        self.updated_at = datetime.utcnow()
