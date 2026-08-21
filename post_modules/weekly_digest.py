import random
from datetime import datetime, timedelta
from typing import List, Dict

# Заглушка для хранения новостей (в будущем можно заменить на реальные данные)
_mock_news = [
    "ЗСУ звільнили ще один населений пункт на Донбасі",
    "Ворог зазнав значних втрат у живій силі та техніці",
    "Міжнародна допомога: новий пакет військової підтримки",
    "Економіка України демонструє стійкість попри війну",
    "Дипломатичний прорив: нові союзники готові допомагати",
]

def get_recent_news(limit: int = 5) -> List[str]:
    """Возвращает последние новости (заглушка)"""
    # В будущем можно брать из базы данных или из posted_links.json
    return random.sample(_mock_news, min(limit, len(_mock_news)))

def generate_weekly_digest() -> str:
    """
    Генерирует дайджест за неделю
    """
    today = datetime.now()
    week_start = (today - timedelta(days=today.weekday())).strftime("%d.%m.%Y")
    week_end = today.strftime("%d.%m.%Y")
    
    lines = [
        f"📌 **ДАЙДЖЕСТ ТИЖНЯ: {week_start} – {week_end}**",
        "",
        "Ключові події за цей тиждень:",
        ""
    ]
    
    news = get_recent_news(5)
    for i, item in enumerate(news, 1):
        lines.append(f"{i}. {item}")
    
    lines.append("")
    lines.append("💬 Яка новина, на вашу думку, була найважливішою?")
    lines.append("#дайджест #тиждень #НАШАСТАЛЬ")
    
    return "\n".join(lines)

def test():
    print("="*60)
    print(generate_weekly_digest())
    print("="*60)

if __name__ == "__main__":
    test()
