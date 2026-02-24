import bcrypt


class BcryptHasher:
    def hash(self, password: str) -> str:
        pwd_bytes = password.encode("utf-8")

        hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt(rounds=12))

        return hashed.decode("utf-8")

    def verify(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
