from typing import Optional
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session
from config.database.session import get_db_session
from review.application.port.product_repository_port import ProductRepositoryPort, ProductRow

class ProductRepositoryImpl(ProductRepositoryPort):
    def __init__(self, session: Session | None = None):
        self.db: Session = session or get_db_session()

    def get(self, source: str, product_id: str) -> Optional[ProductRow]:
        row = self.db.execute(text("""
            SELECT source, source_product_id, analysis_status, review_count
            FROM products
            WHERE source = :s AND source_product_id = :p
            LIMIT 1
        """), {"s": source, "p": product_id}).mappings().first()
        return dict(row) if row else None

    def update_status(self, source: str, product_id: str, status: str, review_count: int = 0) -> None:
        self.db.execute(text("""
            UPDATE products
            SET analysis_status = :st, review_count = :rc, collected_at = NULL
            WHERE source = :s AND source_product_id = :p
        """), {"st": status, "rc": review_count, "s": source, "p": product_id})
        self.db.commit()
