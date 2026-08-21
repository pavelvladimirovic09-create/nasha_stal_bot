import asyncio
import aiohttp
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import InputMediaPhoto

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

bot = Bot(token=settings.TELEGRAM_TOKEN)


async def send_post_to_channel(post_text: str, image_url: str = None) -> bool:
    try:
        await asyncio.sleep(1)
        
        channel_id = int(settings.CHANNEL_ID) if settings.CHANNEL_ID else None
        
        if not channel_id:
            logger.error("❌ CHANNEL_ID не установлен в .env")
            return False
        
        if image_url:
            # Отправляем с изображением
            message = await bot.send_photo(
                chat_id=channel_id,
                photo=image_url,
                caption=post_text,
                parse_mode="HTML"
            )
            logger.info(f"✅ Пост с фото опубликован! ID сообщения: {message.message_id}")
        else:
            # Отправляем без изображения
            message = await bot.send_message(
                chat_id=channel_id,
                text=post_text,
                parse_mode="HTML"
            )
            logger.info(f"✅ Пост опубликован! ID сообщения: {message.message_id}")
        
        return True
        
    except TelegramAPIError as e:
        logger.error(f"❌ Ошибка Telegram API: {e}")
        return False
    except ValueError as e:
        logger.error(f"❌ Неверный CHANNEL_ID: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Неизвестная ошибка: {e}")
        return False


async def test_send():
    test_post = """
🔥 Тестовий пост від бота «НАША СТАЛЬ»

🇺🇦 Тест

💬 Це тестове повідомлення для перевірки роботи бота.

❗ Бот працює коректно!

#тест #НАШАСТАЛЬ
"""
    result = await send_post_to_channel(test_post, "https://img.tsn.ua/cached/220/tsn-dcf0ded845fb4249b37e656be0b1987a/thumbs/608xX/98/3c/acba2c4839acef4abcb41f300acb3c98.jpeg")
    if result:
        print("✅ Тестовый пост с фото отправлен в канал!")
    else:
        print("❌ Ошибка при отправке тестового поста")


if __name__ == "__main__":
    asyncio.run(test_send())
