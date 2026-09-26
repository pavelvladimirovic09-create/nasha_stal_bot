import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Optional

def parse_fuel_prices() -> Optional[Dict]:
    """
    Парсит цены на топливо с index.minfin.com.ua
    """
    try:
        url = "https://index.minfin.com.ua/ua/markets/fuel/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Статус: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем таблицу с ценами
        table = soup.find('table')
        if not table:
            print("❌ Таблица не найдена")
            return None
        
        # Парсим строки таблицы
        rows = table.find_all('tr')
        fuel_data = {}
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 4:
                continue
            
            # Название города или сети
            first_cell = cells[0].text.strip()
            
            # Проверяем, что это город
            if 'Київ' in first_cell or 'Киев' in first_cell:
                city = 'Київ'
            elif 'Дніпро' in first_cell or 'Днепр' in first_cell:
                city = 'Дніпро'
            elif 'Львів' in first_cell:
                city = 'Львів'
            elif 'Харків' in first_cell:
                city = 'Харків'
            else:
                continue
            
            # Собираем цены
            prices = []
            for cell in cells[1:4]:  # Берем первые 3 цены (А-95, ДТ, Газ)
                price_text = cell.text.strip().replace(',', '.').replace('грн', '').strip()
                if price_text and price_text != '-':
                    try:
                        price = float(price_text)
                        prices.append(f"{price:.2f}")
                    except:
                        prices.append("0")
                else:
                    prices.append("0")
            
            if len(prices) >= 3:
                fuel_data[city] = {
                    'a95': prices[0],
                    'dt': prices[1],
                    'gas': prices[2]
                }
                print(f"✅ {city}: А-95 {prices[0]} / ДТ {prices[1]} / Газ {prices[2]}")
        
        return fuel_data if fuel_data else None
        
    except Exception as e:
        print(f"❌ Ошибка парсинга: {e}")
        return None

def get_fuel_prices_for_display() -> Dict:
    """
    Возвращает цены для отображения (с запасным вариантом)
    """
    # Пробуем спарсить свежие цены
    prices = parse_fuel_prices()
    
    if prices:
        return prices
    
    # Запасные цены
    default_prices = {
        "Київ": {"a95": "85.19", "dt": "85.31", "gas": "81.96"},
        "Дніпро": {"a95": "85.00", "dt": "85.00", "gas": "81.00"},
        "Львів": {"a95": "85.00", "dt": "85.73", "gas": "81.00"}
    }
    
    print("⚠️ Использую запасные цены")
    return default_prices

if __name__ == "__main__":
    print("🔍 Парсинг цен на топливо...")
    prices = parse_fuel_prices()
    if prices:
        print("\n📊 Итоговые цены:")
        for city, data in prices.items():
            print(f"  {city}: А-95 {data['a95']} / ДТ {data['dt']} / Газ {data['gas']}")
    else:
        print("❌ Не удалось получить цены")
