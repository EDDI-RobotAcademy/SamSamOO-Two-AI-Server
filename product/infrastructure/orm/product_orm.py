from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from datetime import datetime
from config.database.session import Base
from sqlalchemy.orm import relationship

class ProductORM(Base):
    __tablename__ = 'products'

    source = Column(String(50), primary_key=True, nullable=False)
    source_product_id = Column(String(255), primary_key=True, nullable=False)

    title = Column(Text, nullable=False)
    url = Column(String(512), nullable=False)

    seller_id = Column(Integer, nullable=False)

    # ⭐️ 새로 추가된 필드 1: category ⭐️
    # Enum 값 (예: 'ETC', 'FOOD')을 저장하며, 길이는 Enum 값 최대 길이보다 넉넉하게 설정
    category = Column(String(50), nullable=False, default='ETC')

    # ⭐️ 새로 추가된 필드 2: analysis_status ⭐️
    # Enum 값 (예: 'PENDING', 'COMPLETED')을 저장
    analysis_status = Column(String(50), nullable=False, default='PENDING')

    price = Column(Integer, nullable=True)
    seller = Column(String(255), nullable=True)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=False, default=0)
    collected_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), nullable=False, default='ACTIVE')

    __table_args__ = (
        Index('title_fulltext_idx', 'title', mysql_prefix='FULLTEXT'),
    )

    reviews = relationship("ReviewORM", back_populates="product", cascade="all, delete-orphan")