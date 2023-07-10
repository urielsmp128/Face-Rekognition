from pydantic import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """App Settings"""

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_BUCKET_NAME: str
    DATABASE_CONNECTION_URL: str
    DATABASE_NAME: str
    SECRET: str
    TOKEN_EXP_TIME: int
    TOKEN_EXP_TIME_RESET_PASSWORD: int
    SENDER: str
    CONFIGURATION_SET: str
    SUBJECT: str
    SEARCH_FILE_AWS_S3_DIR: str
    SEARCH_FILE_LIMIT: int
    REKOGNITION_COLLECTION: str
    VERSION: float = 0.1

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()  # type: ignore


settings = get_settings()
