# Todos os models precisam ser importados aqui para o autogenerate do Alembic
from .base import Base
from .user_model import UserOrm

__all__ = ["Base", "UserOrm"]
