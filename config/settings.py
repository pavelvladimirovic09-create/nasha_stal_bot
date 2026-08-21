import os
from dotenv import load_dotenv
from pathlib import Path

from core.sources import get_all_sources

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")
    
    POST_INTERVAL_MINUTES: int = int(os.getenv("POST_INTERVAL_MINUTES", 150))
    MAX_POSTS_PER_DAY: int = int(os.getenv("MAX_POSTS_PER_DAY", 10))
    
    # Используем все источники из core/sources.py
    RSS_SOURCES = get_all_sources()
    
    DATA_DIR = BASE_DIR / "data"
    POSTED_LINKS_FILE = DATA_DIR / "posted_links.json"
    
    @classmethod
    def validate(cls) -> bool:
        errors = []
        if not cls.TELEGRAM_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN не найден в .env")
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY не найден в .env")
        if not cls.CHANNEL_ID:
            errors.append("CHANNEL_ID не найден в .env")
        if errors:
            for error in errors:
                print(f"❌ {error}")
            return False
        print("✅ Все настройки загружены успешно!")
        return True


settings = Settings()
