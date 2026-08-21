import feedparser

url = "https://feeds.bbci.co.uk/ukrainian/news/rss.xml"
feed = feedparser.parse(url)

print(f"📡 Загружено записей: {len(feed.entries)}")

for i, entry in enumerate(feed.entries[:5], 1):
    print(f"\n{i}. {entry.get('title', 'Без заголовка')}")
    print(f"   Ссылка: {entry.get('link', '')}")
