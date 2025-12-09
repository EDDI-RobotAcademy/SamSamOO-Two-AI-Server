from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from account.application.usecase.account_usecase import AccountUseCase
from account.infrastructure.repository.account_repository_impl import AccountRepositoryImpl


router = APIRouter(prefix="/account", tags=["account"])

repo = AccountRepositoryImpl()
account_usecase = AccountUseCase(repo)


class SignupRequest(BaseModel):
    email: str
    nickname: str
    terms_agreed: bool


@router.post("/signup")
async def signup(req: SignupRequest):

    if not req.terms_agreed:
        raise HTTPException(status_code=400, detail="약관에 동의해야 가입할 수 있습니다.")

    account_usecase.create(
        email=req.email,
        nickname=req.nickname,
        terms_agreed=True
    )

    return {"message": "회원가입 완료"}