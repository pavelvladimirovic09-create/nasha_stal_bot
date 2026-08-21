"""
Приоритеты для новостей об Иране
"""

IRAN_KEYWORDS = {
    "іран": 4,
    "иран": 4,
    "iran": 4,
    "тегеран": 4,
    "tehran": 4,
    "ормуз": 3,
    "hormuz": 3,
    "ізраїль": 3,
    "израиль": 3,
    "israel": 3,
    "близький схід": 3,
    "ближний восток": 3,
    "middle east": 3,
    "перська затока": 3,
    "персидский залив": 3,
    "ракет": 3,
    "ракет": 3,
    "missile": 3,
    "дрон": 3,
    "drone": 3,
    "атака": 3,
    "attack": 3,
    "обстріл": 3,
    "strike": 3,
    "загроз": 3,
    "threat": 3,
    "військ": 3,
    "военн": 3,
    "military": 3,
}

IRAN_STOP_WORDS = [
    "футбол", "спорт", "концерт", "шоу", "кіно", "фільм",
    "рецепт", "кулінар", "мода", "краса", "здоров",
]

def is_iran_news(title: str, summary: str) -> bool:
    """Проверяет, относится ли новость к Ирану"""
    text = f"{title} {summary}".lower()
    
    # Проверяем стоп-слова
    for stop in IRAN_STOP_WORDS:
        if stop in text:
            return False
    
    # Проверяем ключевые слова
    for keyword in IRAN_KEYWORDS:
        if keyword in text:
            return True
    
    return False

def get_iran_priority(title: str, summary: str) -> int:
    """Возвращает приоритет новости об Иране (от 1 до 4)"""
    text = f"{title} {summary}".lower()
    priority = 0
    
    for keyword, score in IRAN_KEYWORDS.items():
        if keyword in text:
            priority = max(priority, score)
    
    return priority

def test_iran():
    test_news = [
        "Іран запустив ракети по Ізраїлю",
        "Новий рекорд з футболу в Ірані",
        "Переговори про ядерну програму Ірану",
        "Спорт в Тегерані"
    ]
    
    print("="*60)
    print("Тест фильтра Ирана:")
    for item in test_news:
        is_iran = is_iran_news(item, "")
        priority = get_iran_priority(item, "")
        print(f"{is_iran} (приоритет {priority}): {item}")
    print("="*60)

if __name__ == "__main__":
    test_iran()
