import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Optional, List

from config.settings import settings
from utils.logger import get_logger
from core.rss_collector import get_news, RSSCollector
from core.news_processor import process_news
from core.priority import sort_news_by_priority
from core.iran_priority import is_iran_news, get_iran_priority
from bot.post_formatter import format_post
from bot.dispatcher import send_post_to_channel
from morning.briefing import generate_morning_post
from post_modules.weekly_digest import generate_weekly_digest
from post_modules.monthly_digest import generate_monthly_digest
from post_modules.humanize import add_humanity

logger = get_logger(__name__)

_running = True

# Минимальный приоритет для публикации
MIN_PRIORITY = 2


def create_posts() -> List[str]:
    posts = []
    try:
        logger.info("📡 Сбор новостей...")
        raw_news = get_news(limit_per_source=0)
        
        if not raw_news:
            logger.warning("⚠️ Нет свежих новостей для публикации")
            return []
        
        # Сначала пробуем новости об Украине
        ukraine_news = sort_news_by_priority(raw_news)
        high_priority_news = [item for item in ukraine_news if item.get('priority', 0) >= MIN_PRIORITY]
        
        # Если нет новостей об Украине — берём новости об Иране
        if not high_priority_news:
            logger.info("📡 Новостей об Украине нет, ищем новости об Иране...")
            iran_news = []
            for item in raw_news:
                title = item.get('title', '')
                summary = item.get('summary', '')
                if is_iran_news(title, summary):
                    priority = get_iran_priority(title, summary)
                    item['priority'] = priority
                    item['is_iran'] = True
                    iran_news.append(item)
            
            # Сортируем новости Ирана по приоритету
            iran_news.sort(key=lambda x: x.get('priority', 0), reverse=True)
            high_priority_news = iran_news[:7]
            
            if high_priority_news:
                logger.info(f"📊 Найдено {len(high_priority_news)} новостей об Иране")
        
        if not high_priority_news:
            logger.warning("⚠️ Нет релевантных новостей")
            return []
        
        # Берем до 7 самых важных
        high_priority_news = high_priority_news[:7]
        logger.info(f"📊 Отобрано {len(high_priority_news)} главных новостей")
        
        for i, news_item in enumerate(high_priority_news):
            priority = news_item.get('priority', 0)
            is_iran = news_item.get('is_iran', False)
            topic = "Иран" if is_iran else "Украина"
            logger.info(f"🔄 Обработка новости {i+1}/{len(high_priority_news)} ({topic}, приоритет {priority})...")
            processed = process_news(news_item)
            image = news_item.get('image', '')
            
            if not processed:
                logger.warning(f"⚠️ Не удалось обработать новость {i+1}")
                continue
            
            post = format_post(processed, include_link=False)
            image = processed.get('image', '')
            post = add_humanity(post, post_type="news")
            
            collector = RSSCollector()
            collector.mark_news_as_posted(news_item)
            
            posts.append(post)
            logger.info(f"✅ Пост {i+1} создан успешно ({topic}, приоритет {priority})")
        
        logger.info(f"📊 Всего создано {len(posts)} постов")
        return posts
        
    except Exception as e:
        logger.error(f"❌ Ошибка при создании постов: {e}")
        return []


def publish_post():
    try:
        logger.info("🕐 Запуск плановой публикации...")
        posts = create_posts()
        
        if not posts:
            logger.warning("⚠️ Нет постов для публикации")
            return
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        for i, post in enumerate(posts):
            try:
                if loop.is_running():
                    asyncio.create_task(send_post_to_channel(post, image))
                else:
                    loop.run_until_complete(send_post_to_channel(post))
                logger.info(f"✅ Пост {i+1}/{len(posts)} отправлен на публикацию")
                time.sleep(3)
            except Exception as e:
                logger.error(f"❌ Ошибка при публикации поста {i+1}: {e}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка при публикации: {e}")


def publish_morning():
    try:
        logger.info("🌅 Публикация утреннего дайджеста...")
        post = generate_morning_post()
        post = add_humanity(post, post_type="morning")
        
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                asyncio.create_task(send_post_to_channel(post, image))
            else:
                asyncio.run(send_post_to_channel(post, image))
            logger.info("✅ Утренний дайджест опубликован!")
        except RuntimeError:
            asyncio.run(send_post_to_channel(post, image))
            logger.info("✅ Утренний дайджест опубликован!")
            
    except Exception as e:
        logger.error(f"❌ Ошибка публикации утреннего дайджеста: {e}")


def publish_weekly_digest():
    try:
        logger.info("📌 Публикация еженедельного дайджеста...")
        post = generate_weekly_digest()
        post = add_humanity(post, post_type="digest")
        
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                asyncio.create_task(send_post_to_channel(post, image))
            else:
                asyncio.run(send_post_to_channel(post, image))
            logger.info("✅ Еженедельный дайджест опубликован!")
        except RuntimeError:
            asyncio.run(send_post_to_channel(post, image))
            logger.info("✅ Еженедельный дайджест опубликован!")
            
    except Exception as e:
        logger.error(f"❌ Ошибка публикации еженедельного дайджеста: {e}")


def publish_monthly_digest():
    try:
        logger.info("📊 Публикация ежемесячного дайджеста...")
        post = generate_monthly_digest()
        post = add_humanity(post, post_type="digest")
        
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                asyncio.create_task(send_post_to_channel(post, image))
            else:
                asyncio.run(send_post_to_channel(post, image))
            logger.info("✅ Ежемесячный дайджест опубликован!")
        except RuntimeError:
            asyncio.run(send_post_to_channel(post, image))
            logger.info("✅ Ежемесячный дайджест опубликован!")
            
    except Exception as e:
        logger.error(f"❌ Ошибка публикации ежемесячного дайджеста: {e}")


def start_scheduler():
    global _running
    _running = True
    
    interval = settings.POST_INTERVAL_MINUTES
    logger.info(f"🚀 Запуск планировщика постинга (интервал: {interval} минут)")
    
    schedule.every(interval).minutes.do(publish_post)
    
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
    
    schedule.every(1).minutes.do(publish_post).tag("first_run")
    
    while _running:
        schedule.run_pending()
        time.sleep(10)
        
        if schedule.get_jobs("first_run"):
            for job in schedule.get_jobs("first_run"):
                schedule.cancel_job(job)


def stop_scheduler():
    global _running
    _running = False
    logger.info("⏹️ Планировщик остановлен")


if __name__ == "__main__":
    from utils.logger import setup_logging
    setup_logging()
    logger.info("🧪 Тест планировщика...")
    publish_post()
    logger.info("✅ Тест завершен")
