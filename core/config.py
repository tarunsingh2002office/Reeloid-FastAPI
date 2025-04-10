import os 
from pathlib import Path
# from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# load_dotenv()

# class Settings:
#     MONGODB_URI = os.getenv("MONGODB_URI")
#     BASE_DIR = Path(__file__).resolve().parent.parent
#     MEDIA_URL = "/media/"
#     MEDIA_ROOT = BASE_DIR / "media"
#     STATIC_URL = "static/"
#     CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
#     CELERY_RESULT_BACKEND = MONGODB_URI + "/celery_results"
#     CELERY_TIMEZONE = "UTC"

# settings = Settings()

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

# Instantiate settings
base_settings = BaseAppSettings()
db_settings = DatabaseSettings()
celery_settings = CelerySettings()

if __name__ == "__main__":
    print(base_settings.BASE_DIR)
    print(db_settings.MONGODB_URI)
    print(celery_settings.CELERY_BROKER_URL)