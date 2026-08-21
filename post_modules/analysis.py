import random

_analysis_templates = [
    "Ситуація на фронті демонструє...",
    "З економічної точки зору, це означає...",
    "Політичний контекст цього рішення...",
    "Що далі? Прогноз від НАША СТАЛЬ...",
]

def generate_analysis(post_text: str) -> str:
    """
    Добавляет разбор/мнение к новости
    """
    template = random.choice(_analysis_templates)
    
    lines = [
        "",
        "🧠 **Короткий аналіз від НАША СТАЛЬ:**",
        f"{template} {post_text[:100]}...",
        "",
        "А як думаєте ви? Поділіться думкою в коментарях!",
    ]
    
    return "\n".join(lines)

def test():
    test_post = "ЗСУ зупинили наступ ворога на Донбасі."
    print("="*60)
    print("Оригінальний пост:\n", test_post)
    print("\nЗ доданим аналізом:\n", generate_analysis(test_post))
    print("="*60)

if __name__ == "__main__":
    test()
