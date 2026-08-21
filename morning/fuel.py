import requests
from typing import Dict, Optional
from bs4 import BeautifulSoup
import re

def get_fuel_prices() -> Optional[Dict]:
    """
    Получает цены на топливо с auto.ria.com
    """
    try:
        url = "https://auto.ria.com/uk/average-fuel-prices/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        fuel = {}
        
        # Ищем средние цены по Украине
        price_items = soup.find_all('div', class_='fuel-price-item')
        for item in price_items:
            name_elem = item.find('span', class_='fuel-name')
            price_elem = item.find('span', class_='fuel-price')
            if name_elem and price_elem:
                name = name_elem.text.strip()
                price = price_elem.text.strip().replace('грн', '').strip()
                if '95' in name:
                    fuel['a95'] = price
                elif 'ДТ' in name or 'дизель' in name.lower():
                    fuel['dt'] = price
                elif 'Газ' in name:
                    fuel['gas'] = price
        
        return fuel if fuel else None
    except Exception:
        return None
