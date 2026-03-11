from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")
    base_dir: Path = BASE_DIR
    media_path: str = "media"
    jwt_signing_key: str
    ollama_api_key: str
    openrouter_key: str


settings = Settings()
