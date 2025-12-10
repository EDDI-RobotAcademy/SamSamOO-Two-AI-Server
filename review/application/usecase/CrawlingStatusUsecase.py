from review.domain.service.crawling_status_service import CrawlingStatusService

class CrawlingStatusUsecase:
    def __init__(self, status_service: CrawlingStatusService):
        self._status_service = status_service

    def execute_save(self, status_data):
        """라우터에서 전달된 상태 데이터를 서비스로 전달"""
        self._status_service.update_status(status_data)

    def execute_get(self, product_id: str):
        return self._status_service.get_latest(product_id)
