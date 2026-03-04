from pathlib import Path
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    base_dir: Path = BASE_DIR
    media_path: str = "media"


settings = Settings()
