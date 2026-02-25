from typing import Optional
from uuid import UUID

import pendulum
from jose import JWTError, jwt

from config import settings


class JWTService:
    def __init__(self) -> None:
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.HASHER_ALGORITHM
        self.expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def create_access_token(self, user_uid: UUID) -> dict:
        expires_at = pendulum.now("UTC").add(minutes=self.expire_minutes)
        to_encode = {"sub": str(user_uid), "exp": int(expires_at.timestamp())}
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": self.expire_minutes * 60,
            "expires_at": expires_at,
        }

    def verify_token(self, token: str) -> Optional[UUID]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")
            if user_id is not None:
                return UUID(user_id)
        except JWTError:
            pass

        return None
