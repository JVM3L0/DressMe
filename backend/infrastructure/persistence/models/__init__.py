# Todos os models precisam ser importados aqui para o autogenerate do Alembic
from .base import Base
from .garment_model import GarmentOrm
from .photo_model import PhotoOrm
from .user_model import UserOrm

__all__ = ["Base", "GarmentOrm", "PhotoOrm", "UserOrm"]
