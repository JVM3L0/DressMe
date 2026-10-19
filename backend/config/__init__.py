import tomllib
from pathlib import Path

from dynaconf import Dynaconf, Validator

# Versão da aplicação: fonte única em pyproject.toml (o projeto não é instalado
# como pacote, então importlib.metadata não a encontra)
_PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"
APP_VERSION: str = tomllib.loads(_PYPROJECT.read_text())["project"]["version"]


class Settings(Dynaconf):
    MODE: str
    DATABASE_URL: str
    SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int


settings: Settings = Dynaconf(
    settings_files=["settings.toml"],
    environments=True,
    envvar_prefix=False,
    load_dotenv=True,
    env_switcher="MODE",
    validators=[
        Validator("MODE", default="development"),
        Validator("DATABASE_URL", required=True),
        Validator("ECHO_SQL", default=False),
        # Chave dos tokens JWT: obrigatória, sem default, com ao menos 256 bits
        Validator(
            "SECRET_KEY",
            must_exist=True,
            condition=lambda key: isinstance(key, str) and len(key.encode()) >= 32,
            # Mensagem própria: a padrão do Dynaconf imprime o valor da chave
            messages={"condition": "SECRET_KEY deve ter ao menos 32 bytes"},
        ),
        Validator("JWT_ALGORITHM", default="HS256", is_in=["HS256", "HS384", "HS512"]),
        Validator("ACCESS_TOKEN_EXPIRE_MINUTES", default=15, cast=int, gt=0),
        # Rate limiting (sintaxe da lib `limits`, ex.: "5/minute")
        Validator("RATE_LIMIT_ENABLED", default=True, is_type_of=bool),
        Validator("RATE_LIMIT_STORAGE_URI", default="memory://"),
        Validator("RATE_LIMIT_SIGNUP", default="5/minute"),
    ],
)  # ty:ignore[invalid-assignment]


settings.validators.validate_all()
