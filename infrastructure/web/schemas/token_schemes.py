from pydantic import AwareDatetime, BaseModel


class TokenResponse(BaseModel, from_attributes=True):
    access_token: str
    token_type: str
    expires_in: int
    expires_at: AwareDatetime
