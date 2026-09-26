import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")
    
    POST_INTERVAL_MINUTES: int = int(os.getenv("POST_INTERVAL_MINUTES", 150))
    MAX_POSTS_PER_DAY: int = int(os.getenv("MAX_POSTS_PER_DAY", 10))
    
    RSS_SOURCES = {
        "tsn": "https://tsn.ua/rss/full.rss",
        "bbc_ukraine": "https://feeds.bbci.co.uk/ukrainian/news/rss.xml",
        "bbc_uk": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "unian_eng": "https://rss.unian.net/site/news_eng.rss",
        "unian_rus": "https://rss.unian.net/site/news_rus.rss",
        "dw": "https://rss.dw.com/rdf/rss-en-all",
        "guardian": "https://www.theguardian.com/uk/rss",
        "aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "npr": "https://feeds.npr.org/1001/rss.xml",
        "cnn": "http://rss.cnn.com/rss/cnn_us.rss",
        "cnbc": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "abc": "http://feeds.abcnews.com/abcnews/topstories",
        "nbc": "http://feeds.nbcnews.com/feeds/worldnews",
        "chinadaily": "https://www.chinadaily.com.cn/rss/world_rss.xml",
        "ukrinform": "https://www.ukrinform.ua/rss/",
        "glavred": "https://glavred.net/rss",
        "pravda": "https://www.pravda.com.ua/rss/"
    }
    
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
