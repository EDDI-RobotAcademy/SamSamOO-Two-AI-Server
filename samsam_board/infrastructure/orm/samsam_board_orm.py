from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from config.database.session import Base


class SamsamBoardORM(Base):
    __tablename__ = "samsam_board"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(String(2000), nullable=False)
    writer_nickname = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
