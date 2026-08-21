"""
Модуль для красивого оформления утреннего приветствия
С рамками, разделителями и стильными элементами
"""

import random
from datetime import datetime

# Стильные рамки
FRAMES = [
    "✧ ✧ ✧",
    "✦ ✦ ✦",
    "☆ ☆ ☆",
    "❃ ❃ ❃",
    "✿ ✿ ✿",
    "• ● • ● •",
    "★ ★ ★",
    "༺ ༻",
    "✧༺ ༻✧",
    "☀ ✿ ☀",
]

# Утренние приветствия (стильные)
GREETINGS = [
    "Доброго ранку, Україно! ☀️",
    "З першими променями, наша незламна! 🌅",
    "Світанок над Україною — початок нової перемоги! 🌄",
    "Доброго ранку, країно-герой! 🇺🇦",
    "Новий день — нові можливости! Гарного ранку! 💪",
    "З добрим ранком, сильна Україно! ⚔️",
    "Прокидайся, Україно! Нас чекає день! 🌤️",
    "Ранок — час для перемог! З новим днем! 🏆",
]

# Эмодзи для разных блоков
EMOJIS = {
    "weather": "🌤️",
    "currency": "💰",
    "fuel": "⛽",
    "greeting": "🌅",
    "separator": "•",
}


def get_frame() -> str:
    """Возвращает случайную рамку"""
    return random.choice(FRAMES)


def get_greeting() -> str:
    """Возвращает случайное приветствие"""
    return random.choice(GREETINGS)


def get_date_line() -> str:
    """Возвращает красивую строку с датой"""
    today = datetime.now()
    return today.strftime("📅 %d.%m.%Y")


def get_weekday() -> str:
    """Возвращает день недели на украинском"""
    weekdays = [
        "Понеділок", "Вівторок", "Середа",
        "Четвер", "П'ятниця", "Субота", "Неділя"
    ]
    return weekdays[datetime.now().weekday()]


def style_block(title: str, content: str, emoji: str = "•") -> str:
    """Оформляет блок в красивом стиле"""
    separator = "─" * 30
    return f"""
{emoji} **{title}**
{content}
{separator}"""


def get_morning_header() -> str:
    """Возвращает красивый заголовок для утреннего поста"""
    frame = get_frame()
    greeting = get_greeting()
    date_line = get_date_line()
    weekday = get_weekday()
    
    return f"""
{frame}
{greeting}
{date_line} | {weekday}
{frame}
"""


def style_morning_post(post_text: str) -> str:
    """
    Применяет стилизацию к готовому утреннему посту
    """
    header = get_morning_header()
    
    # Добавляем красивую подпись
    footer = """
    
─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─

💙💛 **З Україною в серці!**
💪 Разом до перемоги!
🇺🇦 **НАША СТАЛЬ**

─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
"""
    
    return f"{header}\n{post_text}\n{footer}"


def test_greeting():
    """Тест стильного приветствия"""
    test_post = """
🌤️ **Погода на сьогодні:**
• Київ: 24°C, ясно
• Одеса: 26°C, мінлива хмарність
• Львів: 22°C, дощ

💰 **Курси валют (НБУ):**
• USD: 44.71 грн
• EUR: 51.71 грн

⛽ **Ціни на пальне:**
• А-95: 85.50 грн
• ДТ: 95.90 грн
"""
    
    print("="*60)
    print("СТИЛЬНЕ УТРЕННЕ ПРИВІТАННЯ")
    print("="*60)
    print(style_morning_post(test_post))
    print("="*60)


if __name__ == "__main__":
    test_greeting()
