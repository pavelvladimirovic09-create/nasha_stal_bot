"""
Очистка кешей старше RETENTION_DAYS дней.
- posted_links.json — dict {link: "YYYY-MM-DD HH:MM"}
- weekly_news.json  — list [{date: "YYYY-MM-DD HH:MM", ...}]
"""
import os
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from utils.logger import get_logger

logger = get_logger(__name__)

KYIV_TZ = ZoneInfo("Europe/Kyiv")
RETENTION_DAYS = 35

POSTED_FILE = "posted_links.json"
WEEKLY_FILE = "weekly_news.json"


def _cutoff() -> datetime:
    return datetime.now(KYIV_TZ) - timedelta(days=RETENTION_DAYS)


def _parse_date(s: str):
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=KYIV_TZ)
        except ValueError:
            continue
    return None


def clean_posted_links():
    if not os.path.exists(POSTED_FILE):
        logger.info("📂 posted_links.json не найден, пропускаем")
        return
    try:
        with open(POSTED_FILE, 'r') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            logger.warning(f"⚠️ posted_links.json не dict: {type(data).__name__}")
            return

        cutoff = _cutoff()
        before = len(data)
        kept = {}
        removed = 0
        for link, ts in data.items():
            dt = _parse_date(ts)
            if dt is None or dt >= cutoff:
                kept[link] = ts
            else:
                removed += 1

        with open(POSTED_FILE, 'w') as f:
            json.dump(kept, f, ensure_ascii=False, indent=2)
        logger.info(f"🧹 posted_links.json: было {before}, удалено {removed}, осталось {len(kept)}")
    except Exception as e:
        logger.error(f"❌ Ошибка очистки posted_links.json: {e}")


def clean_weekly_news():
    if not os.path.exists(WEEKLY_FILE):
        logger.info("📂 weekly_news.json не найден, пропускаем")
        return
    try:
        with open(WEEKLY_FILE, 'r') as f:
            data = json.load(f)
        if not isinstance(data, list):
            logger.warning(f"⚠️ weekly_news.json не list: {type(data).__name__}")
            return

        cutoff = _cutoff()
        before = len(data)
        kept = []
        removed = 0
        for item in data:
            if not isinstance(item, dict):
                kept.append(item)
                continue
            dt = _parse_date(item.get('date', ''))
            if dt is None or dt >= cutoff:
                kept.append(item)
            else:
                removed += 1

        with open(WEEKLY_FILE, 'w') as f:
            json.dump(kept, f, ensure_ascii=False, indent=2)
        logger.info(f"🧹 weekly_news.json: было {before}, удалено {removed}, осталось {len(kept)}")
    except Exception as e:
        logger.error(f"❌ Ошибка очистки weekly_news.json: {e}")


def clean_cache():
    logger.info(f"🧹 Запуск очистки (retention: {RETENTION_DAYS} дней)")
    clean_posted_links()
    clean_weekly_news()
    logger.info("✅ Очистка завершена")


if __name__ == "__main__":
    clean_cache()
