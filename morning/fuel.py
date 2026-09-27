import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

logger = get_logger(__name__)

KYIV_TZ = ZoneInfo("Europe/Kyiv")
CACHE_FILE = "data/fuel_last.json"


def _save_cache(prices: Dict):
    """Сохраняет успешно спарсенные цены в кеш"""
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'w') as f:
            json.dump({
                "prices": prices,
                "saved_at": datetime.now(KYIV_TZ).strftime("%Y-%m-%d %H:%M")
            }, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Цены сохранены в кеш ({CACHE_FILE})")
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения кеша топлива: {e}")


def _load_cache() -> Optional[Dict]:
    """Читает последние успешные цены из кеша"""
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
        saved_at = data.get('saved_at', '?')
        logger.warning(f"⚠️ Использую кеш топлива от {saved_at}")
        return data.get('prices')
    except Exception as e:
        logger.error(f"❌ Ошибка чтения кеша топлива: {e}")
        return None

def get_fuel_prices_for_display() -> Optional[Dict]:
    """
    Парсит цены на топливо с auto.ria.com
    """
    try:
        url = "https://auto.ria.com/uk/toplivo/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            logger.warning(f"⚠️ Не удалось получить цены: статус {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем таблицу с ценами по регионам
        tables = soup.find_all('table')
        
        fuel_data = {}
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 6:
                    # Ищем названия областей
                    region = cells[0].text.strip()
                    
                    # Нам нужны Киевская, Одесская, Львовская области
                    city = None
                    if 'Київська' in region or 'Киевская' in region:
                        city = 'Київ'
                    elif 'Одеська' in region or 'Одесская' in region:
                        city = 'Одеса'
                    elif 'Львівська' in region or 'Львовская' in region:
                        city = 'Львів'
                    
                    if city:
                        # Парсим цены
                        # Колонки: А-95 (индекс 3), ДП (индекс 4), Газ (индекс 5)
                        a95 = cells[3].text.strip().replace(',', '.').replace('грн', '').strip()
                        dp = cells[5].text.strip().replace(',', '.').replace('грн', '').strip()
                        gas = cells[4].text.strip().replace(',', '.').replace('грн', '').strip()
                        
                        # Проверяем, что цены валидны
                        try:
                            float(a95)
                            float(dp)
                            float(gas)
                            fuel_data[city] = {
                                'a95': a95,
                                'dt': dp,
                                'gas': gas
                            }
                            logger.info(f"✅ {city}: А-95 {a95} / ДТ {dp} / Газ {gas}")
                        except:
                            continue
        
        if fuel_data:
            # Если есть все три города - сохраняем в кеш и возвращаем
            if 'Київ' in fuel_data and 'Одеса' in fuel_data and 'Львів' in fuel_data:
                _save_cache(fuel_data)
                return fuel_data
            else:
                # Дополняем недостающие города данными из Киева
                if 'Київ' in fuel_data:
                    for city in ['Одеса', 'Львів']:
                        if city not in fuel_data:
                            fuel_data[city] = fuel_data['Київ'].copy()
                            logger.info(f"⚠️ {city}: скопировано из Киева")
                    _save_cache(fuel_data)
                    return fuel_data
        
        logger.warning("⚠️ Не удалось найти цены на auto.ria.com")
        # Fallback: читаем из кеша
        return _load_cache()
        
    except Exception as e:
        logger.error(f"❌ Ошибка парсинга auto.ria.com: {e}")
        # Fallback: читаем из кеша
        return _load_cache()

def get_fuel_prices() -> Optional[Dict]:
    """
    Возвращает цены на топливо
    """
    return get_fuel_prices_for_display()

if __name__ == "__main__":
    print("🔍 Парсим цены с auto.ria.com...")
    prices = get_fuel_prices_for_display()
    if prices:
        print("✅ Цены получены:")
        for city, data in prices.items():
            print(f"  {city}: А-95 {data['a95']} / ДТ {data['dt']} / Газ {data['gas']}")
    else:
        print("❌ Не удалось получить цены")
