import requests
from typing import Dict, Optional
from bs4 import BeautifulSoup
import re

def get_nbu_rates() -> Optional[Dict]:
    try:
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        rates = {}
        for item in data:
            if item['cc'] in ['USD', 'EUR', 'GBP']:
                rates[item['cc']] = {
                    'rate': float(item['rate']),
                    'date': item['exchangedate']
                }
        return rates
    except Exception:
        return None

def get_black_market() -> Optional[Dict]:
    """
    Получает курсы на черном рынке с finance.i.ua
    """
    try:
        url = "https://finance.i.ua/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        rates = {}
        
        # Ищем курсы валют в таблице
        rows = soup.find_all('tr', class_='currency-row')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                currency = cells[0].text.strip()
                buy = cells[1].text.strip()
                sell = cells[2].text.strip()
                if 'USD' in currency:
                    rates['USD'] = {'buy': buy, 'sell': sell}
                elif 'EUR' in currency:
                    rates['EUR'] = {'buy': buy, 'sell': sell}
        
        return rates if rates else None
    except Exception:
        return None
