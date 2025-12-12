import os
from dotenv import load_dotenv
from celery import Celery

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_DB_BROKER = 0
REDIS_DB_BACKEND = 1

# Celery 연결 URL 구성: redis://:password@host:port/db_number
if REDIS_PASSWORD:
    BROKER_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_BROKER}'
    BACKEND_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_BACKEND}'
else:
    BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_BROKER}'
    BACKEND_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_BACKEND}'


celery_app = Celery(
    'SamSamOO-Two-AI-Server_tasks',
    broker=BROKER_URL,
    backend=BACKEND_URL,
    # Task 함수가 app/tasks/tasks.py에 있다고 가정
    include=['app.tasks.tasks']
)

print(f"Celery Broker configured to: {BROKER_URL.replace(REDIS_PASSWORD, '***')}")
print(f"Celery Backend configured to: {BACKEND_URL.replace(REDIS_PASSWORD, '***')}")