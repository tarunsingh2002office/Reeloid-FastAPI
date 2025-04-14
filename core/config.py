from pathlib import Path
from pydantic_settings import BaseSettings

class BaseAppSettings(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    MEDIA_URL: str = "/media/"
    MEDIA_ROOT: Path = BASE_DIR / "media"
    STATIC_URL: str = "static/"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in the .env file


class DatabaseSettings(BaseSettings):
    MONGODB_URI: str

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in the .env file

class CelerySettings(BaseSettings):
    CELERY_BROKER_URL: str
    CELERY_TIMEZONE: str = "UTC"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in the .env file

class EmailSettings(BaseSettings):
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int
    EMAIL_USE_TLS: bool
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in the .env file

class AppSettings(BaseSettings):
    CELERY_BROKER_URL: str
    EMAIL_PORT: int
    EMAIL_USE_TLS: bool
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in the .env file


class JWTSettings(BaseSettings):
    SUGAR_VALUE: str
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in the .env file


class GoogleAuthSettings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    # GOOGLE_CLIENT_SECRET: str

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in the .env file


class PAYUSettings(BaseSettings):
    PAYU_URL: str
    PAYU_SALT: str
    PAYU_KEY: str
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in the .env file


# Instantiate settings
base_settings = BaseAppSettings()
db_settings = DatabaseSettings()
celery_settings = CelerySettings()
email_settings = EmailSettings()
app_settings = AppSettings()
jwt_settings = JWTSettings()
google_settings = GoogleAuthSettings()
payu_settings = PAYUSettings()

# if __name__ == "__main__":
#     print(base_settings.BASE_DIR)
#     print(db_settings.MONGODB_URI)
#     print(celery_settings.CELERY_BROKER_URL)