import random

# Подписи для постов
SIGNATURES = [
    "Редакція «НАША СТАЛЬ»",
    "Ваша НАША СТАЛЬ",
    "Команда НАША СТАЛЬ",
    "Аналітики НАША СТАЛЬ",
    "Журналісти НАША СТАЛЬ"
]

# Эмодзи для разных типов постов
EMOJIS = {
    "analysis": "🧠",
    "news": "📰",
    "opinion": "💡",
    "digest": "📌",
    "morning": "🌅",
    "warning": "⚠️",
    "victory": "🏆",
    "economy": "📊",
    "military": "⚔️"
}

def add_humanity(post_text: str, post_type: str = "news") -> str:
    """
    Добавляет человечность посту: подпись, эмодзи, приветствие
    """
    emoji = EMOJIS.get(post_type, "📌")
    signature = random.choice(SIGNATURES)
    
    # Добавляем эмодзи в начало (если нет)
    if not post_text.startswith(emoji):
        post_text = f"{emoji} {post_text}"
    
    # Добавляем подпись в конец (если нет)
    if signature not in post_text:
        post_text = f"{post_text}\n\n— {signature}"
    
    return post_text

def get_greeting_for_post() -> str:
    """Случайное приветствие для поста"""
    greetings = [
        "Шановні підписники!",
        "Друзі!",
        "Увага!",
        "Важливо!",
        "Ексклюзивно!"
    ]
    return random.choice(greetings)
