from pathlib import Path
from pydantic_settings import BaseSettings

class BaseAppSettings(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    MEDIA_URL: str = "/media/"
    MEDIA_ROOT: Path = BASE_DIR / "media"
    STATIC_URL: str = "static/"

class DatabaseSettings(BaseSettings):
    MONGODB_URI: str

    class Config:
        env_file = ".env"

class CelerySettings(BaseSettings):
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CELERY_TIMEZONE: str = "UTC"

    @property
    def result_backend(self):
        return f"{self.CELERY_RESULT_BACKEND}/celery_results"

    class Config:
        env_file = ".env"

class EmailSettings(BaseSettings):
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int
    EMAIL_USE_TLS: bool
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str

    class Config:
        env_file = ".env"

class AppSettings(BaseSettings):
    CELERY_BROKER_URL: str
    EMAIL_PORT: int
    EMAIL_USE_TLS: bool
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str

    class Config:
        env_file = ".env"  # Specify the .env file location

class JWTSettings(BaseSettings):
    SUGAR_VALUE: str
    
    class Config:
        env_file = ".env"

class GoogleAuthSettings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    # GOOGLE_CLIENT_SECRET: str

    class Config:    
        env_file = ".env"

class PAYUSettings(BaseSettings):
    PAYU_URL: str
    PAYU_SALT: str
    PAYU_KEY: str
    class Config:
        env_file = ".env"

# Instantiate settings
base_settings = BaseAppSettings()
db_settings = DatabaseSettings()
celery_settings = CelerySettings()
email_settings = EmailSettings()
app_settings = AppSettings()
jwt_settings = JWTSettings()
google_settings = GoogleAuthSettings()

# if __name__ == "__main__":
#     print(base_settings.BASE_DIR)
#     print(db_settings.MONGODB_URI)
#     print(celery_settings.CELERY_BROKER_URL)