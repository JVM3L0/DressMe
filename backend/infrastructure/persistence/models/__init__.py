# Todos os models precisam ser importados aqui para o autogenerate do Alembic
from .base import Base
from .garment_model import GarmentOrm
from .outfit_model import OutfitOrm, outfit_garments
from .photo_model import PhotoOrm
from .user_model import UserOrm

__all__ = ["Base", "GarmentOrm", "OutfitOrm", "PhotoOrm", "UserOrm", "outfit_garments"]
