from uuid import UUID, uuid4

from domain.entities.garment import Garment
from domain.entities.image import ProcessedImage, StoredImage
from domain.entities.photo import Photo
from domain.entities.user import User
from domain.enums.garment_category import GarmentCategory
from domain.exceptions.image import InvalidImageError


def make_user(**overrides) -> User:
    data = {
        "username": "joao",
        "email": "joao@example.com",
        "hashed_password": "hash",
    }
    return User(**(data | overrides))


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: list[User] = []

    async def save(self, user: User) -> User:
        self.users.append(user)
        return user

    async def exists_by_email_or_username(self, email: str, username: str) -> bool:
        return any(
            u.email == email or u.username.lower() == username.lower()
            for u in self.users
        )

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self.users if u.email == email.lower()), None)

    async def get_by_uid(self, uid: UUID) -> User | None:
        return next((u for u in self.users if u.uid == uid), None)


class FakePasswordHasher:
    def __init__(self) -> None:
        self.hashed: list[str] = []

    async def hash(self, password: str) -> str:
        self.hashed.append(password)
        return f"hashed:{password}"

    async def verify(self, password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed:{password}"


class FakeTokenService:
    """Token legível nos testes: `token:<uid>`"""

    def create_access_token(self, user_id: UUID) -> str:
        return f"token:{user_id}"

    def verify_token(self, token: str) -> UUID | None:
        prefix, _, uid = token.partition(":")
        try:
            return UUID(uid) if prefix == "token" else None
        except ValueError:
            return None


def make_stored_image(**overrides) -> StoredImage:
    data = {
        "key": f"photos/{uuid4()}.jpg",
        "content_type": "image/jpeg",
        "width": 300,
        "height": 400,
    }
    return StoredImage(**(data | overrides))


class FakeImageProcessor:
    """Aceita qualquer coisa, exceto conteúdo que comece com `invalid`"""

    async def process(self, data: bytes) -> ProcessedImage:
        if data.startswith(b"invalid"):
            raise InvalidImageError()
        return ProcessedImage(
            data=b"processed:" + data, content_type="image/jpeg", width=300, height=400
        )


class FakeImageStorage:
    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}

    async def save(self, key: str, data: bytes) -> None:
        self.files[key] = data

    async def delete(self, key: str) -> None:
        self.files.pop(key, None)


class _FakeOwnedRepository[T: (Photo, Garment)]:
    def __init__(self) -> None:
        self.items: list[T] = []

    async def save(self, item: T) -> T:
        self.items.append(item)
        return item

    async def get_for_owner(self, uid: UUID, owner_id: UUID) -> T | None:
        return next(
            (i for i in self.items if i.uid == uid and i.owner_id == owner_id), None
        )

    async def delete(self, item: T) -> None:
        self.items = [i for i in self.items if i.uid != item.uid]

    def _by_owner(self, owner_id: UUID) -> list[T]:
        owned = [i for i in self.items if i.owner_id == owner_id]
        return sorted(owned, key=lambda i: i.created_at, reverse=True)


class FakePhotoRepository(_FakeOwnedRepository[Photo]):
    async def list_by_owner(self, owner_id: UUID) -> list[Photo]:
        return self._by_owner(owner_id)


class FakeGarmentRepository(_FakeOwnedRepository[Garment]):
    async def list_by_owner(
        self, owner_id: UUID, category: GarmentCategory | None = None
    ) -> list[Garment]:
        return [
            g
            for g in self._by_owner(owner_id)
            if category is None or g.category == category
        ]
