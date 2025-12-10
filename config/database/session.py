from sqlalchemy import create_engine, QueuePool
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

password = urllib.parse.quote_plus(os.getenv("MYSQL_PASSWORD"))

DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{password}"
    f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
)

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,                    # 연결 풀 크기
    max_overflow=20,                 # 최대 추가 연결 수
    pool_timeout=30,                 # 연결 대기 시간 (초)
    pool_recycle=3600,               # 1시간마다 연결 재생성 (타임아웃 방지)
    pool_pre_ping=True,              # 쿼리 전 연결 확인 (끊어진 연결 자동 재연결)
    echo=False,                      # SQL 로그 출력 (개발 시 True)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db_session():
    return SessionLocal()
