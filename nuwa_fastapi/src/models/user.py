from pydantic import BaseModel


class SignUpModel(BaseModel):
    username: str
    password: str


class SignInModel(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponseModel(BaseModel):
    username: str
