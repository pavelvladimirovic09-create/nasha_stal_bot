"""
Список всех источников RSS для канала НАША СТАЛЬ
Разбит по категориям для удобства управления
"""

# Украинские источники
UKRAINE_SOURCES = {
    "tsn": "https://tsn.ua/rss/full.rss",
    "bbc_ukraine": "https://feeds.bbci.co.uk/ukrainian/news/rss.xml",
    "ukrinform": "https://www.ukrinform.ua/rss/",
    "unian_eng": "https://rss.unian.net/site/news_eng.rss",
    "unian_rus": "https://rss.unian.net/site/news_rus.rss",
}

# Британские источники
UK_SOURCES = {
    "bbc_uk": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "guardian": "https://www.theguardian.com/uk/rss",
}

# Европейские источники
EU_SOURCES = {
    "dw": "https://rss.dw.com/rdf/rss-en-all",
    "aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
}

# Американские источники
US_SOURCES = {
    "npr": "https://feeds.npr.org/1001/rss.xml",
    "cnn": "http://rss.cnn.com/rss/cnn_us.rss",
    "cnbc": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "abc": "http://feeds.abcnews.com/abcnews/topstories",
    "nbc": "http://feeds.nbcnews.com/feeds/worldnews",
}

# Китайские источники
CHINA_SOURCES = {
    "chinadaily": "https://www.chinadaily.com.cn/rss/world_rss.xml",
}

# Все источники в одном словаре
ALL_SOURCES = {
    **UKRAINE_SOURCES,
    **UK_SOURCES,
    **EU_SOURCES,
    **US_SOURCES,
    **CHINA_SOURCES
}

def get_all_sources():
    return ALL_SOURCES

def get_source_categories():
    return {
        "ukraine": UKRAINE_SOURCES,
        "uk": UK_SOURCES,
        "eu": EU_SOURCES,
        "us": US_SOURCES,
        "china": CHINA_SOURCES
    }

if __name__ == "__main__":
    print("📡 Источники по категориям:")
    for category, sources in get_source_categories().items():
        print(f"\n{category}:")
        for name, url in sources.items():
            print(f"  {name}: {url}")
