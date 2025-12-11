from typing import Protocol

class CrawlerQueuePort(Protocol):
    def enqueue_collect(self, source: str, product_id: str) -> str: ...
