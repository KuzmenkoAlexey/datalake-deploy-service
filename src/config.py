from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str
    database_name: str = "database_name"
    debug: bool = False
    jwt_secret: str = "SECRET"
    sentry_url: str = None


settings = Settings()
