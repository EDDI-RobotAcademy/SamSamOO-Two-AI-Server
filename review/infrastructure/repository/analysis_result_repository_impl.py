from sqlalchemy import text
from sqlalchemy.engine import Connection
from review.application.port.analysis_result_repository_port import AnalysisResultRepositoryPort
from sqlalchemy.orm import Session
from config.database.session import get_db_session

class AnalysisResultRepositoryImpl(AnalysisResultRepositoryPort):
    def __init__(self, session: Session | None = None):
        self.db: Session = session or get_db_session()

    def delete_by_product(self, source: str, product_id: str) -> int:
        res = self.db.execute(text("""
            DELETE ar
            FROM analysis_result ar
            JOIN analysis_jobs aj ON ar.job_id = aj.id
            WHERE aj.source = :s AND aj.source_product_id = :p
        """), {"s": source, "p": product_id})
        self.db.commit()
        return res.rowcount or 0
