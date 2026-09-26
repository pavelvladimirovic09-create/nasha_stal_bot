from typing import Dict, Optional
import re

class PostFormatter:
    """Форматирует новости для публикации в Telegram"""
    
    SOURCE_FLAGS = {
        'tsn': '🇺🇦',
        'bbc_ukraine': '🇬🇧',
        'bbc_uk': '🇬🇧',
        'unian_eng': '🇺🇦',
        'unian_rus': '🇺🇦',
        'dw': '🇩🇪',
        'guardian': '🇬🇧',
        'aljazeera': '🇶🇦',
        'npr': '🇺🇸',
        'cnn': '🇺🇸',
        'cnbc': '🇺🇸',
        'abc': '🇺🇸',
        'nbc': '🇺🇸',
        'chinadaily': '🇨🇳',
        'ukrinform': '🇺🇦',
        'glavred': '🇺🇦',
        'pravda': '🇺🇦',
        'sky_news': '🇬🇧',
        'apnews': '🇺🇸',
        'washington_post': '🇺🇸',
        'france24': '🇫🇷',
        'lemonde': '🇫🇷',
    }
    
    SOURCE_LABELS = {
        'tsn': 'TSN.ua',
        'bbc_ukraine': 'BBC Україна',
        'bbc_uk': 'BBC UK',
        'unian_eng': 'UNIAN (англ.)',
        'unian_rus': 'УНІАН (рос.)',
        'dw': 'Deutsche Welle',
        'guardian': 'The Guardian',
        'aljazeera': 'Al Jazeera',
        'npr': 'NPR',
        'cnn': 'CNN',
        'cnbc': 'CNBC',
        'abc': 'ABC News',
        'nbc': 'NBC',
        'chinadaily': 'China Daily',
        'ukrinform': 'Укрінформ',
        'glavred': 'Glavred',
        'pravda': 'Українська правда',
        'sky_news': 'Sky News',
        'apnews': 'AP News',
        'washington_post': 'Washington Post',
        'france24': 'France 24',
        'lemonde': 'Le Monde',
    }
    
    def __init__(self):
        self.flags = self.SOURCE_FLAGS
        self.labels = self.SOURCE_LABELS
    
    def _get_flag(self, source: str) -> str:
        return self.flags.get(source, '🌍')
    
    def _get_label(self, source: str) -> str:
        return self.labels.get(source, source)
    
    def format_post(self, processed_news: Dict, include_link: bool = True) -> str:
        title = processed_news.get('title', 'Без заголовка')
        summary = processed_news.get('summary', '')
        source = processed_news.get('source', 'unknown')
        link = processed_news.get('link', '')
        
        flag = self._get_flag(source)
        label = self._get_label(source)
        
        lines = []
        lines.append(f"{flag} **{label}**")
        lines.append("")
        lines.append(f"📰 **{title}**")
        lines.append("")
        
        if summary:
            # Очищаем summary от лишних пробелов
            clean_summary = ' '.join(summary.split())
            lines.append(clean_summary)
            lines.append("")
        
        if include_link and link:
            lines.append(f"🔗 [Читати далі]({link})")
        
        return "\n".join(lines)

def format_post(processed_news: Dict, include_link: bool = True) -> str:
    formatter = PostFormatter()
    return formatter.format_post(processed_news, include_link)

if __name__ == "__main__":
    test_news = {
        'title': 'Тестова новина',
        'summary': 'Це тестовий опис новини.',
        'source': 'tsn',
        'link': 'https://test.ua'
    }
    print(format_post(test_news))
