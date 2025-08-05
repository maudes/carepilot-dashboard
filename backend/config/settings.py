from pydantic import BaseSettings
import os


# Settings for the application, using Pydantic's BaseSettings 
# for environment variable management
class Settings(BaseSettings):
    DATABASE_URL: str
    env: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env.development" if os.getenv("ENV") == "development" else ".env.production"
        # os.getenv("content") -> map to the content in .env files
        # add os.getenv(default=value) -> in case it returns production wrongly
        # path -> pydantic starts from the root directory

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite://")


settings = Settings()
