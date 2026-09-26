"""
Месячный дайджест: берёт новости из архива за последние 30 дней,
отправляет в OpenAI, получает структурированный пост.
"""
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List, Dict

from utils.logger import get_logger

logger = get_logger(__name__)

KYIV_TZ = ZoneInfo("Europe/Kyiv")
ARCHIVE_FILE = "weekly_news.json"   # общий архив новостей (35 дней)


def get_monthly_news(days: int = 30) -> List[Dict]:
    """Загружает новости из архива за последние N дней (по умолчанию 30)."""
    if not os.path.exists(ARCHIVE_FILE):
        logger.warning("⚠️ Файл архива не найден")
        return []

    try:
        import json
        with open(ARCHIVE_FILE, 'r') as f:
            archive = json.load(f)
    except Exception as e:
        logger.error(f"❌ Ошибка чтения архива: {e}")
        return []

    cutoff = datetime.now(KYIV_TZ) - timedelta(days=days)
    filtered = []
    for item in archive:
        if not isinstance(item, dict):
            continue
        date_str = item.get('date', '')
        if not date_str:
            continue
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M').replace(tzinfo=KYIV_TZ)
            if dt >= cutoff:
                filtered.append(item)
        except ValueError:
            continue

    logger.info(f"📊 Загружено {len(filtered)} новостей за {days} дней (из {len(archive)} в архиве)")
    return filtered


def generate_monthly_digest() -> str:
    """Генерирует месячный дайджест через AI."""
    from openai import OpenAI
    from config.settings import settings

    news = get_monthly_news(30)

    if not news:
        logger.warning("⚠️ Нет новостей за месяц")
        return "📊 <b>ДАЙДЖЕСТ МІСЯЦЯ</b>\n\n⚠️ Новини за цей місяць відсутні"

    # Уникальные заголовки, максимум 80
    titles = []
    seen = set()
    for item in news:
        t = item.get('title', '').strip()
        if not t or t in seen:
            continue
        seen.add(t)
        titles.append(f"- {t} ({item.get('source', '')})")
        if len(titles) >= 80:
            break

    if not titles:
        return "📊 <b>ДАЙДЖЕСТ МІСЯЦЯ</b>\n\n⚠️ Новини за цей місяць відсутні"

    today = datetime.now(KYIV_TZ)
    month_start = (today - timedelta(days=30)).strftime("%d.%m.%Y")
    month_end = today.strftime("%d.%m.%Y")

    prompt = f"""Ты — редактор новостного канала «НАША СТАЛЬ».
Составь дайджест главных событий за месяц ({month_start} – {month_end}).

Вот заголовки новостей за месяц:
{chr(10).join(titles)}

Требования:
- Выбери 7-10 самых важных событий месяца
- Пиши кратко (1-2 предложения на каждое)
- Пиши на украинском языке
- Используй эмодзи
- В конце — короткое резюме месяца одной фразой

Структура:
📊 ДАЙДЖЕСТ МІСЯЦЯ: {month_start} – {month_end}

🔝 Головні події:
1. ...
2. ...

💬 Підсумок: ...
"""

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты — редактор украинского новостного канала."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        digest = response.choices[0].message.content.strip()
        logger.info("✅ AI сгенерировал месячный дайджест")
        digest += "\n\n#дайджест #місяць #НАШАСТАЛЬ"
        return digest
    except Exception as e:
        logger.error(f"❌ Ошибка AI: {e}")
        # Fallback без AI
        lines = [f"📊 <b>ДАЙДЖЕСТ МІСЯЦЯ: {month_start} – {month_end}</b>", ""]
        for i, item in enumerate(news[:10], 1):
            lines.append(f"{i}. {item.get('title', '')} ({item.get('source', '')})")
        return "\n".join(lines)


if __name__ == "__main__":
    print(generate_monthly_digest())
