import asyncio
import aiohttp
import io
import os
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import BufferedInputFile
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)
bot = Bot(token=settings.TELEGRAM_TOKEN)

async def download_image(url: str):
    try:
        logger.info(f"📥 Скачиваем изображение: {url[:80]}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.read()
                    logger.info(f"✅ Изображение скачано: {len(data)} байт")
                    return data
                else:
                    logger.warning(f"⚠️ Ошибка скачивания: статус {response.status}")
                    return None
    except Exception as e:
        logger.error(f"❌ Ошибка скачивания: {e}")
        return None

async def send_post_to_channel(post_text: str, image_url: str = None, image_path: str = None) -> bool:
    """
    Отправляет пост в канал.
    image_url — ссылка на изображение в интернете
    image_path — путь к локальному файлу на сервере
    """
    try:
        await asyncio.sleep(1)
        channel_id = int(settings.CHANNEL_ID) if settings.CHANNEL_ID else None
        if not channel_id:
            logger.error("❌ CHANNEL_ID не установлен в .env")
            return False

        logger.info(f"📤 Отправка в канал {channel_id}")

        # ===== ЛОКАЛЬНОЕ ФОТО =====
        if image_path and os.path.exists(image_path):
            try:
                logger.info(f"📸 Отправка локального фото: {image_path}")
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                photo_file = BufferedInputFile(file=image_data, filename="photo.jpg")
                message = await bot.send_photo(
                    chat_id=channel_id,
                    photo=photo_file,
                    caption=post_text,
                    parse_mode="HTML"
                )
                logger.info(f"✅✅✅ ПОСТ С ЛОКАЛЬНЫМ ФОТО ОПУБЛИКОВАН! ID: {message.message_id}")
                return True
            except Exception as e:
                logger.error(f"❌ Ошибка отправки локального фото: {e}")
                # Продолжаем — попробуем отправить без фото

        # ===== URL ФОТО =====
        if image_url:
            logger.info("📥 Пробуем скачать фото по URL...")
            image_data = await download_image(image_url)
            if image_data:
                try:
                    photo_file = BufferedInputFile(file=image_data, filename="photo.jpg")
                    message = await bot.send_photo(
                        chat_id=channel_id,
                        photo=photo_file,
                        caption=post_text,
                        parse_mode="HTML"
                    )
                    logger.info(f"✅ Пост с фото опубликован! ID: {message.message_id}")
                    return True
                except Exception as e:
                    logger.error(f"❌ Ошибка отправки фото: {e}")

        # ===== БЕЗ ФОТО =====
        logger.info("📤 Отправляем текстовый пост...")
        message = await bot.send_message(
            chat_id=channel_id,
            text=post_text,
            parse_mode="HTML"
        )
        logger.info(f"✅ Пост без фото опубликован! ID: {message.message_id}")
        return True

    except TelegramAPIError as e:
        logger.error(f"❌ Ошибка Telegram API: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
