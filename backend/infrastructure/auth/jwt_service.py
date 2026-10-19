from uuid import UUID

import jwt
import pendulum

# Algoritmos simétricos aceitos e o tamanho mínimo da chave em bytes, que
# deve ser ao menos o tamanho do hash (RFC 7518, seção 3.2). Nunca aceitar
# "none" nem algoritmos assimétricos com a mesma chave.
MIN_SECRET_KEY_BYTES = {"HS256": 32, "HS384": 48, "HS512": 64}


class JWTService:
    def __init__(
        self, secret_key: str, algorithm: str = "HS256", expire_minutes: int = 15
    ) -> None:
        if algorithm not in MIN_SECRET_KEY_BYTES:
            raise ValueError(f"Algoritmo JWT não suportado: {algorithm}")
        min_bytes = MIN_SECRET_KEY_BYTES[algorithm]
        if len(secret_key.encode("utf-8")) < min_bytes:
            raise ValueError(
                f"SECRET_KEY deve ter ao menos {min_bytes} bytes para {algorithm}"
            )
        if expire_minutes <= 0:
            raise ValueError("expire_minutes deve ser positivo")

        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    def create_access_token(self, user_id: UUID) -> str:
        now = pendulum.now("UTC")
        payload = {
            "sub": str(user_id),
            "iat": now,
            "exp": now.add(minutes=self.expire_minutes),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> UUID | None:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"require": ["sub", "exp", "iat"]},
            )
            return UUID(payload["sub"])
        except (jwt.InvalidTokenError, ValueError, TypeError):
            # Token inválido, expirado, adulterado ou com `sub` que não é UUID
            return None
