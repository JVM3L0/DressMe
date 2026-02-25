from dynaconf import Dynaconf, Validator


class Settings(Dynaconf):
    MODE: str
    DATABASE_URL: str
    SECRET_KEY: str
    HASHER_ALGORITHM: str
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
        Validator("ECHO_SQL", default=True),
        Validator("SECRET_KEY", must_exist=True),
        Validator("HASHER_ALGORITHM", default="HS256"),
        Validator("ACCESS_TOKEN_EXPIRE_MINUTES", default=60, cast=int),
    ],
)  # ty:ignore[invalid-assignment]


settings.validators.validate_all()
