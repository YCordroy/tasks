from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: int
    username: str


class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str
