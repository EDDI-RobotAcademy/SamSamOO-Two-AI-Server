from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from config.database.session import get_db_session
from review.application.port.analysis_job_repository_port import AnalysisJobRepositoryPort

class AnalysisJobRepositoryImpl(AnalysisJobRepositoryPort):
    def __init__(self, session: Session | None = None):
        from sqlalchemy.orm import Session
        self.db: Session = session or get_db_session()

    def delete_by_product(self, source: str, product_id: str) -> int:
        res = self.db.execute(text("""
            DELETE FROM analysis_jobs
            WHERE source = :s AND source_product_id = :p
        """), {"s": source, "p": product_id})
        self.db.commit()
        return int(res.rowcount or 0)