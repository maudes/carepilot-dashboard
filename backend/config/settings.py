# For env changes, define all items from env files
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os


# Settings for the application, using Pydantic's BaseSettings
# for environment variable management
class Settings(BaseSettings):
    DATABASE_URL: str
    env: str
    debug: bool = True
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_reload: bool = False
    api_log_level: str = "info"

    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: str = ""

    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"
    mail_from_name: str = "CarePilot Team"
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    use_credentials: bool = True
    validate_certs: bool = True


    '''
    upstash_redis_url: str
    upstash_redis_token: str
    secret_key: str
    weather_api_key: str
    health_news_api_key: str
    '''
    env_file: str = f".env.{os.getenv("ENV", "development")}"
    model_config = ConfigDict(env_file=env_file, extra="allow")
    # ConfigDict(key=value)

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite://")


settings = Settings()
