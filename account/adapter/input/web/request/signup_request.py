from pydantic import BaseModel


class SignupRequest(BaseModel):
    email: str
    nickname: str
    terms_agreed: bool