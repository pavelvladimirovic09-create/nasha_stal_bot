from morning.greeting import get_greeting
from morning.weather import get_all_weather
from morning.currency import get_nbu_rates
from morning.fuel import get_fuel_prices
from morning.image_generator import generate_morning_image
from morning.day_info_loader import get_today_info
import asyncio
from utils.logger import get_logger
from aiogram import Bot
from aiogram.types import BufferedInputFile
from config.settings import settings
from datetime import datetime

logger = get_logger(__name__)

async def send_morning_image():
    """Генерирует и отправляет изображение в Telegram"""
    try:
        logger.info("🌅 Генерация утреннего изображения...")
        
        # Генерируем изображение
        image_path = generate_morning_image()
        logger.info(f"✅ Изображение создано: {image_path}")
        
        # Читаем изображение
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        logger.info(f"📸 Размер изображения: {len(image_data)} байт")
        
        # Отправляем в Telegram
        bot = Bot(token=settings.TELEGRAM_TOKEN)
        channel_id = int(settings.CHANNEL_ID)
        
        photo_file = BufferedInputFile(file=image_data, filename="morning.jpg")
        
        # Основной текст
        caption_parts = []
        caption_parts.append("🌅 Доброго ранку, Україно!")
        caption_parts.append("🇺🇦 НАША СТАЛЬ")
        caption_parts.append("")
        
        # Добавляем информацию о дне (автоматически для каждого дня)
        caption_parts.append(get_today_info())
        
        caption = "\n".join(caption_parts)
        
        message = await bot.send_photo(
            chat_id=channel_id,
            photo=photo_file,
            caption=caption,
            parse_mode="HTML"
        )
        
        logger.info(f"✅ Утреннее изображение отправлено! ID: {message.message_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки утреннего изображения: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def publish_morning_with_image():
    """Запускает отправку утреннего изображения"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_morning_image())
    finally:
        loop.close()

if __name__ == "__main__":
    publish_morning_with_image()
