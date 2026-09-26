import asyncio
import schedule
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, List

from config.settings import settings
from utils.logger import get_logger
from core.rss_collector import get_news, mark_news_as_posted
from core.news_processor import process_news
from bot.post_formatter import format_post
from bot.dispatcher import send_post_to_channel
from morning.briefing import generate_morning_post
from post_modules.weekly_digest import generate_weekly_digest
from post_modules.monthly_digest import generate_monthly_digest
from post_modules.humanize import add_humanity

logger = get_logger(__name__)

_running = True
_loop = None

def get_event_loop():
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop

KYIV_TZ = ZoneInfo("Europe/Kyiv")

def is_working_hours() -> bool:
    now = datetime.now(KYIV_TZ)
    hour = now.hour
    return 7 <= hour < 23

def create_posts() -> List[dict]:
    posts = []
    try:
        logger.info("📡 Сбор новостей...")
        raw_news = get_news(limit_per_source=5)
        
        if not raw_news:
            logger.warning("⚠️ Нет свежих новостей для публикации")
            return []
        
        from core.priority import sort_news_by_priority
        sorted_news = sort_news_by_priority(raw_news)
        sorted_news = sorted_news[:1]
        logger.info(f"📊 Отобрано {len(sorted_news)} главных новостей")
        
        for i, news_item in enumerate(sorted_news):
            priority = news_item.get('priority', 0)
            logger.info(f"🔄 Обработка новости {i+1}/{len(sorted_news)} (приоритет {priority})...")
            processed = process_news(news_item)
            
            if not processed:
                logger.warning(f"⚠️ Не удалось обработать новость {i+1}")
                continue
            
            post_text = format_post(processed, include_link=True)
            post_text = add_humanity(post_text, post_type="news")
            image_url = news_item.get('image', '')
            
            # Добавляем ссылку для отметки
            link = news_item.get('link', '')
            
            posts.append({
                'text': post_text,
                'image': image_url,
                'link': link,
                'title': news_item.get('title', ''),
                'source': news_item.get('source_label', '') 
            })
            logger.info(f"✅ Пост {i+1} создан успешно (приоритет {priority})")
        
        logger.info(f"📊 Всего создано {len(posts)} постов")
        return posts
        
    except Exception as e:
        logger.error(f"❌ Ошибка при создании постов: {e}")
        return []

def send_posts_immediately(posts: List[dict]):
    if not posts:
        return
    
    logger.info(f"📤 Отправка {len(posts)} постов в Telegram...")
    
    loop = get_event_loop()
    
    for i, post_data in enumerate(posts):
        try:
            loop.run_until_complete(
                send_post_to_channel(post_data['text'], post_data['image'])
            )
            logger.info(f"✅ Пост {i+1}/{len(posts)} отправлен")
            
            # Отмечаем новость как отправленную
            if post_data.get('link'):
                mark_news_as_posted(
                    post_data['link'],
                    post_data.get('title', ''),
                    post_data.get('source', '')
                )
            
            time.sleep(2)
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке поста {i+1}: {e}")

def publish_posts_batch():
    if not is_working_hours():
        logger.info("⏰ Нерабочее время (7:00-23:00). Публикация пропущена.")
        return
    
    try:
        logger.info("🕐 Запуск публикации...")
        posts = create_posts()
        if posts:
            send_posts_immediately(posts)
        else:
            logger.warning("⚠️ Нет постов для публикации")
    except Exception as e:
        logger.error(f"❌ Ошибка при публикации: {e}")

def publish_morning():
    try:
        logger.info("🌅 Публикация утреннего дайджеста (изображение)...")
        from morning.briefing_with_image import publish_morning_with_image
        publish_morning_with_image()
        logger.info("✅ Утренний дайджест опубликован!")
    except Exception as e:
        logger.error(f"❌ Ошибка публикации утреннего дайджеста: {e}")

def publish_weekly_digest():
    try:
        logger.info("📌 Публикация еженедельного дайджеста...")
        post = generate_weekly_digest()
        post = add_humanity(post, post_type="digest")
        
        loop = get_event_loop()
        loop.run_until_complete(
            send_post_to_channel(post, image_path="templates/weekly_digest.png")
        )
        logger.info("✅ Еженедельный дайджест с фото опубликован!")
    except Exception as e:
        logger.error(f"❌ Ошибка публикации еженедельного дайджеста: {e}")

def publish_monthly_digest():
    try:
        logger.info("📊 Публикация ежемесячного дайджеста...")
        post = generate_monthly_digest()
        post = add_humanity(post, post_type="digest")
        
        loop = get_event_loop()
        loop.run_until_complete(send_post_to_channel(post))
        logger.info("✅ Ежемесячный дайджест опубликован!")
    except Exception as e:
        logger.error(f"❌ Ошибка публикации ежемесячного дайджеста: {e}")

def start_scheduler():
    global _running
    _running = True
    
    get_event_loop()
    
    schedule.every(10).minutes.do(publish_posts_batch)
    schedule.every().day.at("04:00").do(clean_cache)  # Очистка кэша каждую ночь в 3:00
    logger.info("🚀 Запуск планировщика: 3 поста каждые 10 минут (7:00-23:00 по Киеву)")
    
    schedule.every().day.at("08:00").do(publish_morning)
    logger.info("🌅 Утренний дайджест запланирован на 8:00")
    
    schedule.every().sunday.at("20:00").do(publish_weekly_digest)
    logger.info("📌 Еженедельный дайджест запланирован на воскресенье 20:00")
    
    def is_last_sunday():
        today = datetime.now()
        if today.weekday() != 6:
            return False
        next_week = today + timedelta(days=7)
        return next_week.month != today.month
    
    if is_last_sunday():
        schedule.every().day.at("20:00").do(publish_monthly_digest)
        logger.info("📊 Ежемесячный дайджест запланирован на сегодня 20:00")
    else:
        def check_monthly():
            if is_last_sunday():
                schedule.every().day.at("20:00").do(publish_monthly_digest)
                logger.info("📊 Ежемесячный дайджест запланирован на сегодня 20:00")
        schedule.every().day.at("00:00").do(check_monthly)
        logger.info("📊 Ежемесячный дайджест будет проверяться ежедневно")
    
    while _running:
        schedule.run_pending()
        time.sleep(10)

def stop_scheduler():
    global _running
    _running = False
    logger.info("⏹️ Планировщик остановлен")

if __name__ == "__main__":
    from utils.logger import setup_logging
    setup_logging()
    logger.info("🧪 Тест планировщика...")
    publish_posts_batch()
    logger.info("✅ Тест завершен")
from scheduler.clean_cache import clean_cache
