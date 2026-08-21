"""
Модуль строгого перевода для новостей
Переводит максимально близко к оригиналу, только легкая обработка
"""

import re
from typing import Dict, Optional

def strict_translate(text: str, is_english: bool = False) -> str:
    """
    Строгий перевод: только исправление очевидных ошибок,
    без изменения смысла и стиля
    """
    if not is_english:
        # Если текст уже на украинском — только легкая чистка
        return clean_ukrainian(text)
    
    # Если текст на английском — строгий перевод с сохранением стиля
    return translate_english_strict(text)


def clean_ukrainian(text: str) -> str:
    """Легкая чистка украинского текста"""
    # Убираем лишние пробелы
    text = re.sub(r'\s+', ' ', text)
    
    # Исправляем типичные ошибки (если есть)
    text = text.replace('.,', '.')
    text = text.replace(',,', ',')
    text = text.replace('..', '.')
    
    # Убираем лишние запятые перед союзом "що"
    text = re.sub(r',\s+що', ' що', text)
    text = re.sub(r',\s+як', ' як', text)
    
    return text.strip()


def translate_english_strict(text: str) -> str:
    """
    Строгий перевод с английского на украинский.
    Сохраняет структуру, термины, стиль оригинала.
    """
    # Базовый словарь для строгого перевода (без потери смысла)
    # В реальном боте это будет через OpenAI с жестким промптом
    return f"[Переклад з англійської] {text}"


def get_translation_prompt() -> str:
    """
    Возвращает промпт для OpenAI (строгий перевод)
    """
    return """
Ти — професійний перекладач. Твоє завдання — перекласти текст з англійської на українську максимально близько до оригіналу.

ПРАВИЛА:
1. Зберігай структуру речень
2. Зберігай терміни (назви, імена, дати)
3. Не додавай власних коментарів
4. Не змінюй стиль автора
5. Не скорочуй текст

Перекладай ТІЛЬКИ текст, без додаткових пояснень.
"""


def test_translator():
    """Тест модуля перевода"""
    test_texts = [
        ("Russia launched a missile attack on Kyiv", True),
        ("Українські військові відбили атаку", False),
        ("President Zelensky held a meeting with NATO representatives", True),
    ]
    
    print("="*60)
    print("Тест строгого перевода:")
    for text, is_eng in test_texts:
        result = strict_translate(text, is_eng)
        print(f"\nОригинал: {text}")
        print(f"Результат: {result}")
    print("="*60)


if __name__ == "__main__":
    test_translator()
