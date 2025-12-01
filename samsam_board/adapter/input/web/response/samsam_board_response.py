from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SamsamBoardResponse(BaseModel):
    id: int
    title: str
    content: str
    writer_nickname: Optional[str] = None   # ✅ 추가
    created_at: datetime
    updated_at: datetime
