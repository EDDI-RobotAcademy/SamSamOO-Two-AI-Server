from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text,
    ForeignKeyConstraint, PrimaryKeyConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database.session import Base


class ReviewORM(Base):
    __tablename__ = 'reviews'

    # 복합키: product.source + product.source_product_id
    source = Column(String(50), nullable=False)
    source_product_id = Column(String(255), nullable=False)

    # 리뷰 고유 식별자 (로컬)
    review_id = Column(Integer, autoincrement=True, nullable=False)

    # 리뷰 필드
    reviewer = Column(String(255), nullable=True)
    rating = Column(Float, nullable=True)
    content = Column(Text, nullable=False)

    review_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    collected_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # ---- PK 정의 ----
    __table_args__ = (
        PrimaryKeyConstraint('review_id', 'source', 'source_product_id'),
        ForeignKeyConstraint(
            ['source', 'source_product_id'],
            ['products.source', 'products.source_product_id'],
            ondelete="CASCADE"
        ),
    )

    # ProductORM relationship
    product = relationship("ProductORM", backref="reviews")
