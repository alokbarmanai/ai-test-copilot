import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    db_path: Path = Path(os.getenv("DB_PATH", "data/results.db"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
