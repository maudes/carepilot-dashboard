from pydantic import BaseModel
from typing import Optional


# Use for back-end
class TokenPayload(BaseModel):
    sub: str
    exp: int
    type: str

    @property
    def id(self) -> str:
        return self.sub


# Response data to front-end
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    redirect_to: Optional[str] = None
