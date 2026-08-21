"""
Главный файл запуска бота «НАША СТАЛЬ»
"""

import asyncio
import sys
from pathlib import Path
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config.settings import settings
from utils.logger import setup_logging, get_logger
from scheduler.job_scheduler import publish_post, start_scheduler, stop_scheduler

setup_logging()
logger = get_logger(__name__)

bot = Bot(token=settings.TELEGRAM_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🇺🇦 Вітаю! Я бот каналу «НАША СТАЛЬ».\n\n"
        "📌 Я автоматично публікую свіжі новини.\n"
        "🤖 Команди:\n"
        "/start — це повідомлення\n"
        "/help — довідка\n"
        "/post — опублікувати новину зараз\n"
        "/stats — статистика"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📖 Довідка по боту:\n\n"
        f"⏱️ Інтервал постингу: {settings.POST_INTERVAL_MINUTES} хв\n"
        f"📊 Максимум постів: {settings.MAX_POSTS_PER_DAY} на день\n"
        "📡 Джерела: TSN.ua, BBC Україна, BBC UK, Укрінформ та інші\n\n"
        "🔧 Команди:\n"
        "/post — опублікувати новину зараз\n"
        "/stats — статистика\n"
        "/start — головне меню"
    )


@dp.message(Command("post"))
async def cmd_post(message: types.Message):
    await message.answer("🔄 Починаю публікацію новини...")
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, publish_post)
        await message.answer("✅ Новини опубліковано!")
    except Exception as e:
        logger.error(f"❌ Ошибка при публикации: {e}")
        await message.answer(f"❌ Помилка: {str(e)[:100]}")


@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    try:
        chat = await bot.get_chat(settings.CHANNEL_ID)
        members = await bot.get_chat_member_count(settings.CHANNEL_ID)
        stats = (
            f"📊 Статистика каналу «НАША СТАЛЬ»:\n\n"
            f"👥 Підписників: {members}\n"
            f"📌 Назва: {chat.title}\n"
            f"🔗 Посилання: https://t.me/{chat.username}\n"
            f"⏱️ Інтервал постингу: {settings.POST_INTERVAL_MINUTES} хв\n"
            f"📰 Джерел RSS: {len(settings.RSS_SOURCES)} + Укрінформ (HTML)"
        )
        await message.answer(stats)
    except Exception as e:
        logger.error(f"❌ Ошибка при получении статистики: {e}")
        await message.answer("❌ Не вдалося отримати статистику")


async def main():
    logger.info("🚀 Запуск бота «НАША СТАЛЬ»")
    logger.info(f"📌 Канал: {settings.CHANNEL_ID}")
    logger.info(f"⏱️ Интервал постинга: {settings.POST_INTERVAL_MINUTES} минут")
    
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("✅ Планировщик запущен")
    
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
    finally:
        stop_scheduler()
        await bot.session.close()
        logger.info("👋 Бот завершил работу")


if __name__ == "__main__":
    asyncio.run(main())
