from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class GoogleAuthResponse(BaseModel):
    authorization_url: str


class GoogleCallbackRequest(BaseModel):
    code: str
