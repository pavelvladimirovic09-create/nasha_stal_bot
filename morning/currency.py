import requests
from typing import Dict, Optional

def get_nbu_rates() -> Optional[Dict]:
    """
    Получает официальные курсы валют с API НБУ
    и добавляет спред для покупки/продажи
    """
    try:
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        rates = {}
        for item in data:
            if item['cc'] in ['USD', 'EUR', 'GBP']:
                rate = float(item['rate'])
                # Спред 0.5%: покупка ниже, продажа выше
                spread = rate * 0.005
                rates[item['cc']] = {
                    'buy': f"{rate - spread:.2f}",
                    'sell': f"{rate + spread:.2f}",
                    'date': item['exchangedate']
                }
        return rates
    except Exception:
        return None
