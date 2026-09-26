import json
import os
from datetime import datetime, timedelta
from typing import List, Dict
from utils.logger import get_logger

logger = get_logger(__name__)

WEEKLY_FILE = "weekly_news.json"

def get_weekly_news(days: int = 7) -> List[Dict]:
    """Загружает новости за последние N дней (по умолчанию 7)"""
    if not os.path.exists(WEEKLY_FILE):
        logger.warning("⚠️ Файл архива новостей не найден")
        return []

    try:
        from zoneinfo import ZoneInfo
        KYIV_TZ = ZoneInfo("Europe/Kyiv")
        cutoff = datetime.now(KYIV_TZ) - timedelta(days=days)

        with open(WEEKLY_FILE, 'r') as f:
            news = json.load(f)

        filtered = []
        for item in news:
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

        logger.info(f"📊 Загружено {len(filtered)} новостей за {days} дней (из {len(news)} в архиве)")
        return filtered
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки архива: {e}")
        return []

def clear_weekly_news():
    """Очищает недельный архив"""
    try:
        with open(WEEKLY_FILE, 'w') as f:
            json.dump([], f)
        logger.info("🗑️ Недельный архив очищен")
    except Exception as e:
        logger.error(f"❌ Ошибка очистки недельного архива: {e}")

def generate_weekly_digest() -> str:
    """
    Генерирует дайджест за неделю через AI
    """
    from openai import OpenAI
    from config.settings import settings
    
    # Загружаем новости
    news = get_weekly_news()
    
    if not news:
        logger.warning("⚠️ Нет новостей за неделю")
        return "📊 <b>ДАЙДЖЕСТ ТИЖНЯ</b>\n\n⚠️ Новини за цей тиждень відсутні"
    
    # Формируем список заголовков
    titles = []
    for item in news[:50]:  # Берем максимум 50
        title = item.get('title', '')
        source = item.get('source', '')
        if title:
            titles.append(f"- {title} ({source})")
    
    if not titles:
        return "📊 <b>ДАЙДЖЕСТ ТИЖНЯ</b>\n\n⚠️ Новини за цей тиждень відсутні"
    
    # Даты недели
    today = datetime.now()
    week_start = (today - timedelta(days=today.weekday())).strftime("%d.%m.%Y")
    week_end = today.strftime("%d.%m.%Y")
    
    # Промпт для AI
    prompt = f"""Ты — редактор новостного канала «НАША СТАЛЬ». 
Составь дайджест главных новостей за неделю ({week_start} – {week_end}).

Вот заголовки новостей за неделю:
{chr(10).join(titles)}

Требования:
- Выбери 5-7 самых важных событий
- Напиши кратко (1-2 предложения на каждое)
- Пиши на украинском языке
- Используй эмодзи для наглядности
- Добавь в конце вопрос для обсуждения
- Формат: список с номерами

Структура:
📊 ДАЙДЖЕСТ ТИЖНЯ: {week_start} – {week_end}

🔝 Ключові події:
1. ...
2. ...

💬 Яка новина найважливіша?
"""
    
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты — редактор украинского новостного канала."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        digest = response.choices[0].message.content.strip()
        logger.info("✅ AI сгенерировал дайджест")
        
        # Добавляем хештеги
        digest += "\n\n#дайджест #тиждень #НАШАСТАЛЬ"
        
        # Архив НЕ очищаем — он нужен для месячного дайджеста
        return digest
        
    except Exception as e:
        logger.error(f"❌ Ошибка AI: {e}")
        # Если AI не работает — возвращаем простой список
        lines = [f"📊 <b>ДАЙДЖЕСТ ТИЖНЯ: {week_start} – {week_end}</b>", ""]
        for i, item in enumerate(news[:7], 1):
            title = item.get('title', '')
            source = item.get('source', '')
            lines.append(f"{i}. {title} ({source})")
        return "\n".join(lines)

if __name__ == "__main__":
    print(generate_weekly_digest())
