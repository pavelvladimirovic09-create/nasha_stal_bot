import logging
import sys
from datetime import datetime
import os

def setup_logging(log_level=logging.INFO):
    """Настройка системы логирования"""
    
    # Создаём папку для логов, если её нет
    os.makedirs("logs", exist_ok=True)
    
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    log_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(log_format, date_format)
    
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Вывод в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Вывод в файл
    try:
        file_handler = logging.FileHandler(
            filename=f"logs/bot_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"⚠️ Не удалось создать файл лога: {e}")
    
    # Отключаем шум от библиотек
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Возвращает логгер с именем модуля"""
    return logging.getLogger(name)

if __name__ == "__main__":
    setup_logging()
    logger = get_logger(__name__)
    logger.info("✅ Логгер работает!")
    logger.warning("⚠️ Тестовое предупреждение")
