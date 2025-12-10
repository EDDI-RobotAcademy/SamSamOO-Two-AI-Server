import os

from config.database.session import Base, engine
from samsam_danawa.adapter.danawa_router import router as danawa_router
from social_oauth.adapter.input.web.google_oauth2_router import authentication_router
from config.env_loader import load_env
from product_analysis.adapter.input.web.product_analysis_router import analysis_router
from review.adapter.input.web.review_router import review_router
from product.adapter.input.web.product_router import product_router
from dashboard.adapter.input.web.dashboard_router import dashboard_router
from account.adapter.input.web.account_router import account_router

load_env()

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
os.environ["TORCH_USE_CUDA_DSA"] = "1"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:3000",  # Next.js 프론트 엔드 URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용
    allow_credentials=True,      # 쿠키 허용
    allow_methods=["*"],         # 모든 HTTP 메서드 허용
    allow_headers=["*"],         # 모든 헤더 허용
)

# Router 등록


app.include_router(danawa_router, prefix="/market", tags=["Danawa"])
app.include_router(authentication_router, prefix="/authentication")
app.include_router(review_router, prefix="/review")
app.include_router(product_router, prefix="/product")
app.include_router(analysis_router, prefix="/analysis")
app.include_router(account_router, prefix="/account")
app.include_router(dashboard_router, prefix="/dashboard")

# 앱 실행
if __name__ == "__main__":
    import uvicorn
    host = os.getenv("APP_HOST")
    port = int(os.getenv("APP_PORT"))
    uvicorn.run(app, host=host, port=port)
