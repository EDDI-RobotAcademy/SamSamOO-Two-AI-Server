from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from datetime import datetime
from config.database.session import Base


class ProductORM(Base):
    __tablename__ = 'products'

    source = Column(String(50), primary_key=True, nullable=False)
    source_product_id = Column(String(255), primary_key=True, nullable=False)

    title = Column(Text, nullable=False)
    url = Column(String(512), nullable=False)

    seller_id = Column(Integer, nullable=False)

    price = Column(Integer, nullable=True)
    seller = Column(String(255), nullable=True)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=False, default=0)
    collected_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), nullable=False, default='ACTIVE')

    __table_args__ = (
        Index('title_fulltext_idx', 'title', mysql_prefix='FULLTEXT'),
    )
