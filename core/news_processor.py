import json
from typing import Dict, Optional
from openai import OpenAI
from core.translator import strict_translate

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class NewsProcessor:
    """Обработчик новостей с использованием OpenAI"""
    
    SYSTEM_PROMPT = """Ти — професійний перекладач і журналіст.
ПРАВИЛА:
1. Перекладай максимально близько до оригіналу.
2. Не змінюй стиль і структуру тексту.
3. Не додавай власних коментарів.
Твоє завдання — переписувати новини у живому, емоційному стилі, але без фейків.

Якщо новина англійською — переклади її на українську.

Правила:
1. Зберігай фактичну точність
2. Додай емоційного забарвлення
3. Пиши коротко, динамічно
4. Використовуй активний стан

Формат відповіді — JSON з полями:
{
    "title": "Емоційний заголовок (до 10 слів)",
    "summary": "Суть новини (2 речення)",
    "importance": "Чому це важливо (1 речення)",
    "tags": ["тег1", "тег2"]
}"""
    
    def __init__(self):
        self.client = client
        
    def process_news(self, raw_news: Dict) -> Optional[Dict]:
        try:
            source_label = raw_news.get('source_label', 'Невідоме джерело')
            is_english = raw_news.get('is_english', False)
            
            lang_hint = "Новина англійською мовою. Переклади її на українську." if is_english else ""
            
            user_prompt = f"""Новина з джерела {source_label}:

Заголовок: {raw_news.get('title', 'Без заголовка')}

Текст новини:
{raw_news.get('summary', 'Опис відсутній')}

{lang_hint}
Перепиши цю новину у живому, емоційному стилі для Telegram-каналу.
Відповідь має бути у форматі JSON."""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content.strip()
            processed = json.loads(result_text)
            
            processed['source'] = raw_news.get('source')
            processed['source_label'] = raw_news.get('source_label')
            processed['link'] = raw_news.get('link')
            processed['published'] = raw_news.get('published')
            
            logger.info(f"✅ Оброблено новину: {processed.get('title', 'Без заголовка')}")
            return processed
            
        except Exception as e:
            logger.error(f"❌ Помилка при обробці новини: {e}")
            return None


def process_news(raw_news: Dict) -> Optional[Dict]:
    processor = NewsProcessor()
    return processor.process_news(raw_news)


def test_processor():
    from core.rss_collector import get_news
    from utils.logger import setup_logging
    
    setup_logging()
    
    logger.info("🧪 Запуск тесту обробника новин (з перекладом)...")
    raw_news = get_news(limit_per_source=1)
    
    if not raw_news:
        logger.warning("⚠️ Немає новин для обробки")
        return
    
    logger.info(f"📰 Тестова новина: {raw_news[0]['title']}")
    processed = process_news(raw_news[0])
    
    if processed:
        print("\n" + "="*50)
        print("📰 ОБРОБЛЕНА НОВИНА")
        print("="*50)
        print(f"🔥 {processed.get('title', 'Без заголовка')}")
        print(f"📍 Джерело: {processed.get('source_label', 'Невідоме')}")
        print(f"💬 {processed.get('summary', 'Опис відсутній')}")
        print(f"❗ {processed.get('importance', 'Важливість не вказана')}")
        print(f"🏷️ Теги: {', '.join(processed.get('tags', []))}")
        print("="*50)
    else:
        logger.error("❌ Не вдалося обробити новину")


if __name__ == "__main__":
    test_processor()
