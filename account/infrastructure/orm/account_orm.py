from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from config.database.session import Base

class AccountORM(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    nickname = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    terms_agreed = Column(Boolean, default=False)
    terms_agreed_at = Column(DateTime, nullable=True)
