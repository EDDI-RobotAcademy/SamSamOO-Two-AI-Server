import json
import uuid
from fastapi import APIRouter, Response, Request, Cookie
from fastapi.responses import RedirectResponse

from account.application.usecase.account_usecase import AccountUseCase
from account.infrastructure.repository.account_repository_impl import AccountRepositoryImpl
from config.redis_config import get_redis
from social_oauth.application.usecase.google_oauth2_usecase import GoogleOAuth2UseCase
from social_oauth.infrastructure.service.google_oauth2_service import GoogleOAuth2Service

authentication_router = APIRouter()
service = GoogleOAuth2Service()
account_repository = AccountRepositoryImpl()
account_usecase = AccountUseCase(account_repository)
google_usecase = GoogleOAuth2UseCase(service)

redis_client = get_redis()


@authentication_router.get("/google")
async def redirect_to_google():
    url = google_usecase.get_authorization_url()
    print("[DEBUG] Redirecting to Google:", url)
    return RedirectResponse(url)

@authentication_router.get("/google/redirect")
async def process_google_redirect(
    response: Response,
    code: str,
    state: str | None = None
):
    print("[DEBUG] /google/redirect called")
    print("code:", code)
    print("state:", state)

    result = google_usecase.fetch_user_profile(code, state or "")
    profile = result["profile"]
    access_token = result["access_token"]
    print("profile:", profile)

    # 계정 생성/조회
    account = account_usecase.create_or_get_account(
        profile.get("email"),
        profile.get("name")
    )

    # session_id 생성
    session_id = str(uuid.uuid4())
    print("[DEBUG] Generated session_id:", session_id)

    # 4. Redis에 저장 (user_id + access_token)
    redis_client.set(
        f"session:{session_id}",
        json.dumps({
            "user_id": account.id,
            "access_token": access_token.access_token  # <-- 객체가 아닌 문자열
        }),
        ex=6 * 60 * 60  # 6시간
    )

    # HTTP-only 쿠키 발급
    redirect_response = RedirectResponse("http://localhost:3000")
    redirect_response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=6 * 60 * 60
    )

    print("[DEBUG] Cookie set in RedirectResponse directly")
    return redirect_response

@authentication_router.get("/status")
async def auth_status(request: Request, session_id: str | None = Cookie(None)):
    print("[DEBUG] /status called")
    print("[DEBUG] Request headers:", request.headers)
    print("[DEBUG] Received session_id cookie:", session_id)

    if not session_id:
        return {"logged_in": False}

    redis_key = f"session:{session_id}"
    session_data = redis_client.get(redis_key)

    if not session_data:
        return {"logged_in": False}

    # bytes → str
    if isinstance(session_data, bytes):
        session_data = session_data.decode("utf-8")

    session_dict = json.loads(session_data)
    user_id = session_dict.get("user_id")

    #계정 정보 불러오기
    account = account_repository.find_all_by_id([user_id])

    if not account:
        return {"logged_in": False}

    account = account[0]

    #이메일, 이름 포함해서 리턴
    return {
        "logged_in": True,
        "user_id": account.id,
        "email": account.email,
        "nickname": account.nickname
    }

@authentication_router.post("/logout")
async def logout(response: Response, session_id: str | None = Cookie(None)):
    print("[DEBUG] logout called")
    print("[DEBUG] session_id:", session_id)

    if session_id:
        redis_key = f"session:{session_id}"
        deleted = redis_client.delete(redis_key)
        print("[DEBUG] Redis deleted:", deleted, redis_key)

        response.delete_cookie("session_id")
        print("[DEBUG] Cookie deleted")

    return {"message": "logged out"}

