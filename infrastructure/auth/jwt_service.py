from typing import Optional
from uuid import UUID

import pendulum
from jose import JWTError, jwt


class JWTService:
    def __init__(
        self, secret_key: str, algorithm: str = "HS256", expire_minutes: int = 15
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    def create_access_token(self, user_id: UUID) -> str:
        expire_at = pendulum.now("UTC").add(minutes=self.expire_minutes)
        to_encode = {"sub": str(user_id), "exp": expire_at}
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[UUID]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")
            if user_id is not None:
                return UUID(user_id)
        except JWTError:
            pass

        return None
