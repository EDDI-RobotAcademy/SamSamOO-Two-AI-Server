import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.database.session import Base, engine
from samsam_board.adapter.input.web.samsam_board_router import samsam_board_router
from samsam_naver.adapter.naver_router import router as naver_router
from social_oauth.adapter.input.web.google_oauth2_router import authentication_router
load_dotenv()

app = FastAPI()

# CORS 설정
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # 개발 단계에서는 * 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router 등록
app.include_router(naver_router, prefix="/market-data")
app.include_router(samsam_board_router, prefix="/board")
app.include_router(authentication_router, prefix="/authentication")


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("APP_HOST")
    port = int(os.getenv("APP_PORT"))
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="0.0.0.0", port=33333)
