from dynaconf import Dynaconf, Validator


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
    ],
)  # ty:ignore[invalid-assignment]


settings.validators.validate_all()
