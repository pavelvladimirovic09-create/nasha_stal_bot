from datetime import datetime, timedelta
import random
from typing import List

_mock_news = [
    "ЗСУ звільнили звільнили 5 населених пунктів",
    "Ворог втратив понад 10 000 окупантів",
    "Міжнародна допомога: танки, артилерія, ППО",
    "Україна отримала статус кандидата в ЄС",
    "Енергетична безпека: Україна готується до зими",
]

def get_monthly_news(limit: int = 5) -> List[str]:
    return random.sample(_mock_news, min(limit, len(_mock_news)))

def generate_monthly_digest() -> str:
    """
    Генерирует дайджест за месяц
    """
    today = datetime.now()
    month_name = today.strftime("%B")
    year = today.strftime("%Y")
    
    lines = [
        f"📊 **ДАЙДЖЕСТ МІСЯЦЯ: {month_name} {year}**",
        "",
        "Головні події за останні 30 днів:",
        ""
    ]
    
    news = get_monthly_news(5)
    for i, item in enumerate(news, 1):
        lines.append(f"{i}. {item}")
    
    lines.append("")
    lines.append("🇺🇦 Разом до Перемоги!")
    lines.append("#дайджест #місяць #НАШАСТАЛЬ")
    
    return "\n".join(lines)

def test():
    print("="*60)
    print(generate_monthly_digest())
    print("="*60)

if __name__ == "__main__":
    test()
