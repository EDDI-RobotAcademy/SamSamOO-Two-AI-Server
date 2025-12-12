from typing import Optional
from uuid import uuid4
from review.application.port import CrawlerQueuePort

class RecollectReviewsUseCase:
    def __init__(
        self,
        deleter,
        product_repo,
        crawler_queue: Optional[CrawlerQueuePort] = None,  # ✅ 여기!
    ):
        self.deleter = deleter
        self.product_repo = product_repo
        self.crawler_queue = crawler_queue

    def execute(self, source: str, product_id: str) -> dict:
        deleted = self.deleter.execute(source, product_id)

        self.product_repo.update_status(
            source=source, product_id=product_id, status="CRAWLING", review_count=0
        )

        if self.crawler_queue is not None:
            task_id = self.crawler_queue.enqueue_collect(source, product_id)  # ✅ 경고 사라짐
        else:
            task_id = f"dryrun-{uuid4().hex[:8]}"

        return {"message": "재수집 요청 완료", "deleted": deleted, "task_id": task_id}
