from markdown_it.presets import default
from dynaconf import Dynaconf, Validator


class Settings(Dynaconf):
    MODE: str
    DATABASE_URL: str


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
    ],
)  # ty:ignore[invalid-assignment]


settings.validators.validate_all()
