from pydantic import BaseModel


class TokenResponse(BaseModel):
    """
    登录成功后返回的 Token
    """

    access_token: str
    token_type: str = "bearer"