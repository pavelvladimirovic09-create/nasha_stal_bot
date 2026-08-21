from morning.greeting import get_greeting
from morning.weather import get_all_weather
from morning.currency import get_nbu_rates, get_black_market
from morning.fuel import get_fuel_prices
from morning.greeting_styler import style_morning_post, get_frame, get_morning_header
import random

CITY_NAMES = {
    "kyiv": "Київ",
    "odesa": "Одеса",
    "lviv": "Львів"
}

def get_fallback_fuel():
    return {'a95': '85.50', 'dt': '95.90', 'gas': '43.50'}

def get_fallback_black_market():
    return {
        'USD': {'buy': '44.80', 'sell': '45.10'},
        'EUR': {'buy': '51.80', 'sell': '52.20'}
    }

def generate_morning_post():
    # Получаем данные
    weather = get_all_weather()
    rates = get_nbu_rates()
    black = get_black_market()
    if not black:
        black = get_fallback_black_market()
    fuel = get_fuel_prices()
    if not fuel or not fuel.get('a95'):
        fuel = get_fallback_fuel()
    
    # Формируем основную часть поста (без приветствия)
    lines = []
    
    # Погода
    if weather:
        lines.append("🌤️ **Погода на сьогодні:**")
        for key, data in weather.items():
            city = CITY_NAMES.get(key, key)
            lines.append(f"• **{city}:** {data['temp']}, {data['description']}")
        lines.append("")
    
    # Курсы валют
    if rates:
        lines.append("💰 **Курси валют (НБУ):**")
        for currency, data in rates.items():
            lines.append(f"• {currency}: {data['rate']:.2f} грн")
        lines.append("")
    
    # Черный рынок
    if black:
        lines.append("💱 **Чорний ринок:**")
        for currency, data in black.items():
            lines.append(f"• {currency}: купівля {data['buy']} / продаж {data['sell']}")
        lines.append("")
    
    # Топливо
    if fuel:
        lines.append("⛽ **Ціни на пальне:**")
        lines.append(f"• А-95: {fuel.get('a95', 'н/д')} грн")
        lines.append(f"• ДТ: {fuel.get('dt', 'н/д')} грн")
        lines.append(f"• Газ: {fuel.get('gas', 'н/д')} грн")
        lines.append("")
    
    # Хештеги
    lines.append("#ранок #Україна #НАШАСТАЛЬ #погода #курс #пальне")
    
    # Основной текст поста
    post_body = "\n".join(lines)
    
    # Применяем стилизацию (красивое приветствие + рамки)
    styled_post = style_morning_post(post_body)
    
    return styled_post

def test():
    print("="*60)
    print(generate_morning_post())
    print("="*60)

if __name__ == "__main__":
    test()
