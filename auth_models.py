from pydantic import BaseModel, Field

class AuthBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)

class AuthCreate(AuthBase):
    password: str = Field(..., min_length=3, max_length=50)

class AuthUpdate(AuthCreate):
    pass

class AuthLogin(AuthCreate):
    pass

class Auth(AuthBase):

    class Config:
        from_attributes = True

class TokenInfo(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True