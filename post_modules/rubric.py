import random

# Список рубрик
RUBRICS = {
    "frontline": "⚔️ **ФРОНТ**",
    "politics": "🏛️ **ПОЛІТИКА**",
    "economy": "📊 **ЕКОНОМІКА**",
    "analysis": "🧠 **АНАЛІТИКА**",
    "opinion": "💡 **ДУМКА**",
    "humanity": "❤️ **ЛЮДЯНІСТЬ**",
    "victory": "🏆 **ПЕРЕМОГА**",
    "warning": "⚠️ **УВАГА**",
    "diplomacy": "🤝 **ДИПЛОМАТІЯ**",
    "technology": "💻 **ТЕХНОЛОГІЇ**",
}

# Теги для постов
TAGS = {
    "frontline": ["#фронт", "#ЗСУ", "#війна"],
    "politics": ["#політика", "#дипломатія", "#влада"],
    "economy": ["#економіка", "#бізнес", "#фінанси"],
    "analysis": ["#аналітика", "#прогноз", "#думка"],
    "victory": ["#Перемога", "#ЗСУ", "#Україна"],
    "warning": ["#увага", "#небезпека", "#безпека"],
}

def get_rubric(title: str, category: str = "analysis") -> str:
    """Возвращает рубрику для поста"""
    rubric = RUBRICS.get(category, "📌 **НОВИНИ**")
    return f"{rubric}\n"

def get_tags(category: str = "analysis") -> str:
    """Возвращает теги для поста"""
    tags = TAGS.get(category, ["#новини", "#Україна"])
    return " ".join(tags)

def suggest_category(title: str) -> str:
    """Предлагает категорию на основе заголовка"""
    title_lower = title.lower()
    if any(word in title_lower for word in ["фронт", "зсу", "обстріл", "наступ", "окупант"]):
        return "frontline"
    elif any(word in title_lower for word in ["політик", "вибори", "партія", "закон"]):
        return "politics"
    elif any(word in title_lower for word in ["економік", "бізнес", "фінанс", "ціна"]):
        return "economy"
    elif any(word in title_lower for word in ["перемог", "звільнен", "звитяг"]):
        return "victory"
    else:
        return "analysis"
