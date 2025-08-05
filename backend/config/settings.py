from pydantic_settings import BaseSettings
import os


# Settings for the application, using Pydantic's BaseSettings 
# for environment variable management
class Settings(BaseSettings):
    DATABASE_URL: str
    env: str = "development"
    debug: bool = True
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_reload: bool = False
    api_log_level: str = "info"
    secret_key: str
    weather_api_key: str
    health_news_api_key: str

    class Config:
        env_file = ".env.development" if os.getenv("ENV", "development") == "development" else ".env.production"
        # os.getenv("content") -> map to the content in .env files
        # add os.getenv(default=value) -> in case it returns production wrongly
        # path -> pydantic starts from the root directory
        extra = "allow"

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite://")


settings = Settings()
