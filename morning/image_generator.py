from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")
import os
from morning.blue_section import draw_blue_section
from morning.yellow_section import draw_yellow_section

# ============================================
# НАСТРОЙКИ И ШРИФТЫ
# ============================================

def setup_fonts():
    """Загружает шрифты"""
    try:
        fonts = {
            'title': ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44),
            'text': ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26),
            'big': ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24),
            'small': ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18),
            'header': ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32),
            'tiny': ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16),
            'subheader': ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22),
            'medium': ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28),
        }
    except:
        fonts = {
            'title': ImageFont.load_default(),
            'text': ImageFont.load_default(),
            'big': ImageFont.load_default(),
            'small': ImageFont.load_default(),
            'header': ImageFont.load_default(),
            'tiny': ImageFont.load_default(),
            'subheader': ImageFont.load_default(),
            'medium': ImageFont.load_default(),
        }
    return fonts

# ============================================
# ПОЛУЧЕНИЕ ДАННЫХ
# ============================================

def get_all_data():
    """Получает все данные для утреннего дайджеста"""
    from morning.weather import get_all_weather
    from morning.currency import get_nbu_rates
    from morning.fuel import get_fuel_prices
    
    # Погода
    weather_raw = get_all_weather()
    weather_data = {'cities': []}
    city_names = {"kyiv": "Київ", "odesa": "Одеса", "lviv": "Львів"}
    for key, data in weather_raw.items():
        if key in city_names:
            weather_data['cities'].append({
                'name': city_names[key],
                'temp': data.get('temp', ''),
                'condition': data.get('description', '')
            })
    
    # Курсы НАЦБАНК с покупкой и продажей (НОВАЯ СТРУКТУРА)
    rates = get_nbu_rates()
    currency_data = {'currencies': []}
    if rates:
        for curr, data in rates.items():
            currency_data['currencies'].append({
                'name': curr,
                'buy': data.get('buy', ''),
                'sell': data.get('sell', '')
            })
    
    # Топливо — берём среднее по 3 городам (Київ, Одеса, Львів)
    fuel_raw = get_fuel_prices()
    fuel_data = {'fuels': []}
    if fuel_raw:
        # fuel_raw = {'Київ': {'a95': '88.86', 'dt': ..., 'gas': ...}, ...}
        fuel_keys = ['a95', 'dt', 'gas']       # только нужные (без a92)
        fuel_names = {'a95': 'А-95', 'dt': 'Дизель', 'gas': 'Автогаз'}

        for key in fuel_keys:
            prices = []
            for city, city_data in fuel_raw.items():
                val = city_data.get(key)
                if val:
                    try:
                        prices.append(float(val))
                    except (ValueError, TypeError):
                        pass
            if prices:
                avg = sum(prices) / len(prices)
                fuel_data['fuels'].append({
                    'name': fuel_names[key],
                    'price': f"{avg:.2f}"
                })
    
    # Дата
    months_ua = {
        'January': 'Січня', 'February': 'Лютого', 'March': 'Березня',
        'April': 'Квітня', 'May': 'Травня', 'June': 'Червня',
        'July': 'Липня', 'August': 'Серпня', 'September': 'Вересня',
        'October': 'Жовтня', 'November': 'Листопада', 'December': 'Грудня'
    }
    days_ua = {
        'Monday': 'Понеділок', 'Tuesday': 'Вівторок', 'Wednesday': 'Середа',
        'Thursday': 'Четвер', 'Friday': "П'ятниця",
        'Saturday': 'Субота', 'Sunday': 'Неділя'
    }
    
    now = datetime.now(KYIV_TZ)
    day_num = now.strftime('%d')
    month = months_ua.get(now.strftime('%B'), now.strftime('%B'))
    year = now.strftime('%Y')
    date_str = f"{day_num} {month} {year}"
    day_str = days_ua.get(now.strftime('%A'), now.strftime('%A'))
    war_day = f"{(now - datetime(2022, 2, 24, tzinfo=KYIV_TZ)).days}-й день війни"
    
    return {
        'weather': weather_data,
        'currency': currency_data,
        'fuel': fuel_data,
        'date': date_str,
        'day': day_str,
        'war': war_day
    }

# ============================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================

def generate_morning_image(weather_data=None, currency_data=None, fuel_data=None):
    template_path = "templates/morning_template.jpg"
    
    if not os.path.exists(template_path):
        print(f"⚠️ Шаблон не найден: {template_path}")
        return None
    
    # Загружаем шаблон
    img = Image.open(template_path).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Загружаем шрифты
    fonts = setup_fonts()
    
    # Получаем данные
    if weather_data is None or currency_data is None or fuel_data is None:
        data = get_all_data()
    else:
        data = {
            'weather': weather_data,
            'currency': currency_data,
            'fuel': fuel_data,
            'date': '',
            'day': '',
            'war': ''
        }
    
    width, height = img.size
    center_x = width // 2
    
    # ===== СИНИЙ ФОН (ЖЕЛТЫЙ ТЕКСТ) =====
    y_after_blue = draw_blue_section(draw, center_x, fonts, data)
    
    # ===== ЖЕЛТЫЙ ФОН (СИНИЙ ТЕКСТ) =====
    draw_yellow_section(draw, center_x, fonts, data, y_after_blue)
    
    output_path = "/tmp/morning_digest.png"
    img.save(output_path)
    return output_path

if __name__ == "__main__":
    path = generate_morning_image()
    if path:
        print(f"✅ Изображение создано: {path}")
    else:
        print("❌ Ошибка создания изображения")
