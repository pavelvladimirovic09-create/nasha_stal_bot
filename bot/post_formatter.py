from typing import Dict
from datetime import datetime


class PostFormatter:
    """Форматировщик постов с флагом страны"""
    
    # Флаги для источников
    SOURCE_FLAGS = {
        'tsn': '🇺🇦',
        'bbc_ukraine': '🇬🇧',
        'bbc_uk': '🇬🇧',
        'unian': '🇺🇦',
        'dw': '🇩🇪',
        'guardian': '🇬🇧',
        'aljazeera': '🇶🇦',
        'bellingcat': '🇳🇱',
        'npr': '🇺🇸',
        'cnn': '🇺🇸',
        'cnbc': '🇺🇸',
        'abc': '🇺🇸',
        'nbc': '🇺🇸',
        'chinadaily': '🇨🇳',
        'ukrinform': '🇺🇦',
        'cgtn': '🇨🇳',
        'rada': '🇺🇦'
    }
    
    def _get_flag(self, source: str) -> str:
        """Возвращает флаг для источника"""
        return self.SOURCE_FLAGS.get(source, '🌍')
    
    def format_post(self, processed_news: Dict) -> str:
        """Форматирует пост с флагом страны"""
        title = processed_news.get('title', 'Новина без заголовка')
        summary = processed_news.get('summary', 'Опис відсутній')
        importance = processed_news.get('importance', 'Без коментарів')
        tags = processed_news.get('tags', ['новини'])
        source = processed_news.get('source', 'unknown')
        
        # Получаем флаг
        flag = self._get_flag(source)
        
        # Формируем пост с флагом
        post = (
            f"{flag}\n\n"
            f"🔥 {title}\n\n"
            f"💬 {summary}\n\n"
            f"❗ {importance}\n\n"
            f"#{' #'.join(tags[:3])}"
        )
        return post


def format_post(processed_news: Dict, include_link: bool = False) -> str:
    formatter = PostFormatter()
    return formatter.format_post(processed_news)


def test_formatter():
    print("🧪 Тест форматировщика с флагом...")
    test_news = {
        'source': 'tsn',
        'title': 'ЗСУ зупинили наступ на Донбасі',
        'summary': 'Українські військові відбили атаку. Ворог втратив техніку.',
        'importance': 'Це змінює ситуацію на фронті.',
        'tags': ['фронт', 'донбас', 'зсу']
    }
    print("\n" + "="*50)
    print(format_post(test_news))
    print("="*50)


if __name__ == "__main__":
    test_formatter()
