import feedparser
import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class RSSCollector:
    """Сборщик новостей с усиленным фильтром (только война)"""
    
    KEYWORDS = [
        # ... (оставляем как есть)
    ]
    
    STOP_WORDS = [
        # ... (оставляем как есть)
    ]
    
    # ФЛАГИ СТРАН ДЛЯ ИСТОЧНИКОВ
    SOURCE_FLAGS = {
        'tsn': '🇺🇦',
        'bbc_ukraine': '🇬🇧',
        'bbc_uk': '🇬🇧',
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
        'unian_eng': '🇺🇦',
        'unian_rus': '🇺🇦',
    }
    
    def __init__(self):
        self.sources = settings.RSS_SOURCES
        self.posted_links_file = settings.POSTED_LINKS_FILE
        self.posted_links = self._load_posted_links()
        self.keywords_pattern = re.compile(
            r'(' + '|'.join(self.KEYWORDS) + r')', 
            re.IGNORECASE
        )
    
    def _get_flag(self, source_name: str) -> str:
        return self.SOURCE_FLAGS.get(source_name, '🌍')
    
    def _load_posted_links(self) -> List[str]:
        if not self.posted_links_file.exists():
            return []
        try:
            with open(self.posted_links_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('links', [])
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_posted_links(self) -> None:
        self.posted_links_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.posted_links_file, 'w', encoding='utf-8') as f:
            json.dump({'links': self.posted_links}, f, ensure_ascii=False, indent=2)
    
    def _is_posted(self, link: str) -> bool:
        return link in self.posted_links
    
    def _mark_as_posted(self, link: str) -> None:
        if link not in self.posted_links:
            self.posted_links.append(link)
            self._save_posted_links()
    
    def _is_relevant(self, title: str, summary: str) -> bool:
        text = f"{title} {summary}".lower()
        if any(stop in text for stop in self.STOP_WORDS):
            return False
        result = bool(self.keywords_pattern.search(text))
        if result and ("україн" in text or "війн" in text or "war" in text):
            return True
        return result
    
    def _clean_summary(self, summary: str) -> str:
        clean = re.sub(r'<[^>]+>', '', summary)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()
    
    def _get_source_label(self, source_name: str) -> str:
        labels = {
            'tsn': 'TSN.ua',
            'bbc_ukraine': 'BBC Україна',
            'bbc_uk': 'BBC UK',
            'dw': 'Deutsche Welle',
            'guardian': 'The Guardian',
            'aljazeera': 'Al Jazeera',
            'bellingcat': 'Bellingcat',
            'npr': 'NPR',
            'cnn': 'CNN',
            'cnbc': 'CNBC',
            'abc': 'ABC News',
            'nbc': 'NBC News',
            'chinadaily': 'China Daily',
            'ukrinform': 'Укрінформ',
            'unian_eng': 'УНІАН (англ.)',
            'unian_rus': 'УНІАН (рос.)',
        }
        return labels.get(source_name, source_name)
    
    def _parse_ukrinform(self) -> List[Dict]:
        news_list = []
        try:
            logger.info("📡 Парсинг Укрінформ (HTML)...")
            url = "https://www.ukrinform.ua/"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            with requests.Session() as session:
                response = session.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    return []
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('a', class_='title')[:10]
                for article in articles:
                    title = article.text.strip()
                    link = article.get('href')
                    if not link:
                        continue
                    if not link.startswith('http'):
                        link = f"https://www.ukrinform.ua{link}"
                    if self._is_posted(link) or not self._is_relevant(title, ""):
                        continue
                    news_list.append({
                        'source': 'ukrinform',
                        'title': title,
                        'link': link,
                        'summary': title,
                        'published': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'source_label': self._get_source_label('ukrinform'),
                        'flag': self._get_flag('ukrinform'),
                        'is_english': False
                    })
                logger.info(f"✅ Укрінформ: загружено {len(news_list)} новостей")
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга Укрінформа: {e}")
        return news_list
    
    def fetch_news(self, limit_per_source: int = 0) -> List[Dict]:
        all_news = []
        cutoff_time = datetime.now() - timedelta(hours=48)
        skipped_count = 0
        
        for source_name, source_url in self.sources.items():
            try:
                logger.info(f"📡 Парсинг {source_name}: {source_url}")
                feed = feedparser.parse(source_url)
                if feed.bozo:
                    logger.warning(f"⚠️ Ошибка {source_name}: {feed.bozo_exception}")
                    continue
                if not feed.entries:
                    continue
                
                count = 0
                for entry in feed.entries[:25]:
                    link = entry.get('link', '')
                    if not link or self._is_posted(link):
                        continue
                    title = entry.get('title', '')
                    summary = self._clean_summary(entry.get('summary', ''))
                    if not self._is_relevant(title, summary):
                        skipped_count += 1
                        continue
                    published = entry.get('published')
                    if published:
                        try:
                            pub_time = datetime(*entry.published_parsed[:6])
                            if pub_time < cutoff_time:
                                continue
                        except (AttributeError, TypeError):
                            pass
                    
                    # Извлекаем изображение
                    image = ''
                    for link_entry in entry.get('links', []):
                        if link_entry.get('type', '').startswith('image/'):
                            image = link_entry.get('href', '')
                            break
                    
                    all_news.append({
                        'source': source_name,
                        'title': title,
                        'link': link,
                        'summary': summary[:500],
                        'image': image,
                        'published': published or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'source_label': self._get_source_label(source_name),
                        'flag': self._get_flag(source_name),
                        'is_english': source_name in ['bbc_uk', 'dw', 'guardian', 'aljazeera', 'npr', 'cnn', 'cnbc', 'abc', 'nbc', 'chinadaily', 'unian_eng']
                    })
                    count += 1
                    if limit_per_source > 0 and count >= limit_per_source:
                        break
                logger.info(f"✅ {source_name}: загружено {count} релевантных новостей")
            except Exception as e:
                logger.error(f"❌ Ошибка {source_name}: {e}")
        
        ukrinform_news = self._parse_ukrinform()
        all_news.extend(ukrinform_news[:limit_per_source if limit_per_source > 0 else 10])
        
        logger.info(f"📊 Всего: {len(all_news)} релевантных (пропущено {skipped_count})")
        return all_news
    
    def mark_news_as_posted(self, news_item: Dict) -> None:
        link = news_item.get('link')
        if link:
            self._mark_as_posted(link)


def get_news(limit_per_source: int = 0) -> List[Dict]:
    collector = RSSCollector()
    return collector.fetch_news(limit_per_source)


def test_collector():
    from utils.logger import setup_logging
    setup_logging()
    logger.info("🧪 Тест RSS-сборщика...")
    news = get_news(limit_per_source=0)
    if not news:
        logger.warning("⚠️ Новостей не найдено")
    else:
        logger.info(f"✅ Найдено {len(news)} новостей")
        for i, item in enumerate(news[:10], 1):
            print(f"\n{i}. {item['flag']} {item['source_label']}")
            print(f"   📌 {item['title']}")
            print(f"   🔗 {item['link']}")
    return news


if __name__ == "__main__":
    test_collector()
