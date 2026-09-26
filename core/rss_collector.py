import feedparser
import re
import requests
import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List, Dict
from utils.logger import get_logger

logger = get_logger(__name__)

POSTED_FILE = "posted_links.json"
KYIV_TZ = ZoneInfo("Europe/Kyiv")
RETENTION_DAYS = 35


def _now_str() -> str:
    return datetime.now(KYIV_TZ).strftime("%Y-%m-%d %H:%M")


def load_posted_links() -> dict:
    """Загружает кеш. Старый формат (list/set) конвертирует в dict."""
    if not os.path.exists(POSTED_FILE):
        return {}
    try:
        with open(POSTED_FILE, 'r') as f:
            data = json.load(f)

        if isinstance(data, dict):
            return data

        if isinstance(data, (list, tuple)):
            # Старый формат. Помечаем как "старое" — выпадет при первой чистке
            old_date = (datetime.now(KYIV_TZ) - timedelta(days=RETENTION_DAYS)).strftime("%Y-%m-%d %H:%M")
            converted = {item: old_date for item in data if isinstance(item, str)}
            logger.info(f"🔄 Конвертировано {len(converted)} старых ссылок в новый формат")
            return converted

        return {}
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки кеша: {e}")
        return {}


def save_posted_links():
    try:
        with open(POSTED_FILE, 'w') as f:
            json.dump(POSTED_LINKS, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения кэша: {e}")


POSTED_LINKS = load_posted_links()
logger.info(f"📂 Загружено {len(POSTED_LINKS)} ссылок из кэша")

SOURCES = {
    # Украина
    'tsn': 'https://tsn.ua/rss/full.rss',
    'bbc_ukraine': 'https://feeds.bbci.co.uk/ukrainian/news/rss.xml',
    'unian_eng': 'https://rss.unian.net/site/news_eng.rss',
    'unian_rus': 'https://rss.unian.net/site/news_rus.rss',
    'glavred': 'https://glavred.net/rss',
    'pravda': 'https://www.pravda.com.ua/rss/',
    
    # Британия
    'bbc_uk': 'https://feeds.bbci.co.uk/news/world/rss.xml',
    'guardian': 'https://www.theguardian.com/uk/rss',
    'sky_news': 'https://feeds.skynews.com/feeds/rss/home.xml',
    
    # Европа
    'dw': 'https://rss.dw.com/rdf/rss-en-all',
    'aljazeera': 'https://www.aljazeera.com/xml/rss/all.xml',
    'france24': 'https://www.france24.com/en/rss',
    'lemonde': 'https://www.lemonde.fr/rss/une.xml',
    
    # США
    'npr': 'https://feeds.npr.org/1001/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/cnn_us.rss',
    'cnbc': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
    'abc': 'http://feeds.abcnews.com/abcnews/topstories',
    'nbc': 'http://feeds.nbcnews.com/feeds/worldnews',
    'washington_post': 'https://feeds.washingtonpost.com/rss/world',
    
    # Китай
}

def get_news(limit_per_source: int = 1) -> List[Dict]:
    all_news = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for name, url in SOURCES.items():
        try:
            logger.info(f"📡 Парсинг {name}: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                logger.warning(f"⚠️ {name}: статус {response.status_code}")
                continue
            
            feed = feedparser.parse(response.content)
            count = 0
            for entry in feed.entries[:limit_per_source * 3]:
                if count >= limit_per_source:
                    break
                
                link = entry.get('link', '')
                title = entry.get('title', '').strip()
                
                if not title:
                    continue
                
                # Проверяем по ссылке ИЛИ по заголовку
                if link in POSTED_LINKS:
                    continue
                
                # Проверяем, не было ли уже такой новости по заголовку
                title_hash = f"title_{title}"
                if title_hash in POSTED_LINKS:
                    continue
                
                summary = entry.get('summary', '').strip()
                summary = re.sub(r'<[^>]+>', '', summary)
                
                all_news.append({
                    'source': name,
                    'source_label': name,
                    'title': title,
                    'summary': summary[:300] if summary else title,
                    'link': link,
                    'image': '',
                    'published': entry.get('published', ''),
                    'flag': 'world',
                    'is_english': name in ['bbc_uk', 'guardian', 'dw', 'aljazeera', 'npr', 'cnn', 'cnbc', 'abc', 'nbc', 'washington_post', 'sky_news', 'france24', 'lemonde']
                })
                count += 1
                logger.info(f"✅ {name}: загружено {count} новостей")
        except Exception as e:
            logger.error(f"❌ {name}: {e}")
    
    logger.info(f"📊 Всего новостей: {len(all_news)}")
    return all_news

def mark_news_as_posted(link: str, title: str = '', source: str = ''):
    POSTED_LINKS[link] = _now_str()
    save_posted_links()
    save_weekly_news(link, title, source)
    logger.info(f"✅ Новость сохранена: {link[:50]}...")

def save_weekly_news(link: str, title: str = '', source: str = ''):
    """Сохраняет новость в недельный архив"""
    import json, os
    from datetime import datetime
    
    WEEKLY_FILE = "weekly_news.json"
    
    try:
        if os.path.exists(WEEKLY_FILE):
            with open(WEEKLY_FILE, 'r') as f:
                weekly = json.load(f)
        else:
            weekly = []
        
        weekly.append({
            'link': link,
            'title': title,
            'source': source,
            'date': datetime.now(KYIV_TZ).strftime('%Y-%m-%d %H:%M')
        })
        
        with open(WEEKLY_FILE, 'w') as f:
            json.dump(weekly, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения в недельный архив: {e}")
