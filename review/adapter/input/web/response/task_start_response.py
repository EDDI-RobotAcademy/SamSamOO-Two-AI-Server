from typing import Optional

from pydantic import BaseModel


class TaskStartResponse(BaseModel):
    """
    비동기 크롤링/분석 작업이 성공적으로 시작되었음을 클라이언트에게 알리는 응답 모델입니다.
    클라이언트는 이 응답의 정보를 사용하여 작업 상태를 폴링(Polling)할 수 있습니다.
    """
    task_id: str
    platform: str
    product_id: str
    message: str
    polling_url: Optional[str] = None
