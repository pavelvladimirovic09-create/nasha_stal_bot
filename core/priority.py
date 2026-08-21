"""
Приоритеты новостей для канала НАША СТАЛЬ
Только о войне в Украине и связанных событиях
"""

# Украинские источники (получают бонус +1)
UKRAINE_SOURCES = ['tsn', 'bbc_ukraine', 'ukrinform', 'unian_eng', 'unian_rus']

PRIORITY_KEYWORDS = {
    # Максимальный приоритет (5) — прямые боевые действия
    "зсу": 5, "всу": 5, "наступ": 5, "контрнаступ": 5,
    "фронт": 5, "обстріл": 5, "ракет": 5, "дрон": 5,
    "байрактар": 5, "himars": 5, "starlink": 5,
    "атака": 5, "звільнен": 5, "освобожден": 5,
    "удар": 5, "втрат": 5, "поранен": 5, "загибл": 5,
    
    # Высокий приоритет (4) — Украина, Россия, война
    "україн": 4, "украин": 4, "київ": 4, "киев": 4,
    "донбас": 4, "донбасс": 4, "харків": 4, "харьков": 4,
    "одес": 4, "херсон": 4, "запоріж": 4, "російс": 4,
    "российс": 4, "путін": 4, "кремль": 4, "москв": 4,
    "війна": 4, "война": 4, "військ": 4, "войск": 4,
    "оборон": 4, "захист": 4, "армія": 4, "армия": 4,
    
    # Средний приоритет (3) — международная помощь, санкции
    "санкц": 3, "допомог": 3, "помощ": 3, "нато": 3,
    "nato": 3, "євросоюз": 3, "евросоюз": 3, "трамп": 3,
    "байден": 3, "зеленськ": 3, "зеленский": 3,
    "залужний": 3, "сирський": 3, "буданов": 3,
    
    # Низкий приоритет (2) — экономика, энергетика
    "зернов": 2, "зерно": 2, "продоволь": 2,
    "безпек": 2, "енерг": 2, "газ": 2, "нафт": 2,
}

REQUIRED_WORDS = [
    "україн", "украин", "російс", "российс",
    "війн", "войн", "war", "ukraine", "russia"
]

STOP_WORDS = [
    "пиво", "beer", "вино", "wine", "рецепт", "кулінар", "кулинар",
    "фото", "зірка", "звезда", "шоу", "концерт", "фестиваль",
    "музык", "музик", "пісн", "песн", "кліп", "фильм", "кіно",
    "мода", "стиль", "краса", "красота", "косметик", "макіяж",
    "спорт", "футбол", "теніс", "баскетбол", "хокей", "чемпіонат",
    "ген", "днк", "наук", "історичн", "историчн", "легенд",
    "археолог", "розкопк", "раскопк", "скарб", "клад",
    "автомобіль", "автомобиль", "авто", "запорожець",
    "відпочин", "отдых", "туризм", "подорож", "путешеств",
    "лайфхак", "lifehack", "здоров", "здоровье",
    "одруж", "заміж", "женить", "весіл", "свадьб", "розлучен",
    "діти", "дет", "лікарн", "больниц", "медицин",
    "соціальн", "социальн", "автомоб", "япон", "япони",
    "іран", "ирану", "ліс", "пожеж", "пожар",
    "демократ", "республікан", "праймеріз", "вибори"
]

def is_ukraine_source(source: str) -> bool:
    """Проверяет, является ли источник украинским"""
    return source in UKRAINE_SOURCES

def calculate_priority(title: str, summary: str, source: str = '') -> int:
    text = f"{title} {summary}".lower()
    
    for stop in STOP_WORDS:
        if stop in text:
            return 0
    
    has_required = False
    for word in REQUIRED_WORDS:
        if word in text:
            has_required = True
            break
    
    if not has_required:
        return 0
    
    priority = 0
    for keyword, score in PRIORITY_KEYWORDS.items():
        if keyword in text:
            priority = max(priority, score)
    
    # Бонус +1 для украинских источников
    if is_ukraine_source(source) and priority > 0:
        priority += 1
    
    if priority == 0 and has_required:
        priority = 1
    
    return priority


def sort_news_by_priority(news_list: list) -> list:
    scored_news = []
    for item in news_list:
        title = item.get('title', '')
        summary = item.get('summary', '')
        source = item.get('source', '')
        priority = calculate_priority(title, summary, source)
        
        if priority > 0:
            item['priority'] = priority
            scored_news.append(item)
    
    scored_news.sort(key=lambda x: x.get('priority', 0), reverse=True)
    return scored_news


def test_priority():
    test_news = [
        {'title': 'ЗСУ зупинили наступ на Донбасі', 'summary': 'Бої тривають', 'source': 'tsn'},
        {'title': 'Японські автогіганти під загрозою', 'summary': 'Вплив війни', 'source': 'guardian'},
        {'title': 'Росія обстріляла Харків', 'summary': 'Є жертви', 'source': 'bbc_ukraine'},
        {'title': 'Діти без батьків у лікарнях', 'summary': 'Соціальна проблема', 'source': 'cnn'},
        {'title': 'США надають допомогу Україні', 'summary': 'Новий пакет', 'source': 'unian_eng'},
        {'title': 'Трамп закликав до миру', 'summary': 'Політичні заяви', 'source': 'bbc_uk'},
    ]
    
    sorted_news = sort_news_by_priority(test_news)
    
    print("="*60)
    print("Приоритеты новостей (украинские +1):")
    print("="*60)
    for item in sorted_news:
        print(f"Приоритет {item.get('priority', 0)}: {item['title']} ({item.get('source', '')})")
    print("="*60)


if __name__ == "__main__":
    test_priority()
