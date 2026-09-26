from PIL import Image, ImageDraw, ImageFont
from morning.fuel import get_fuel_prices_for_display

def draw_yellow_section(draw, center_x, fonts, data, start_y):
    """
    Рисует всё на желтом фоне (синим текстом)
    """
    BLUE = (0, 50, 140)
    
    # ===== ПОДНИМАЕМ ВЕСЬ БЛОК =====
    y_pos = start_y + 20 + 30 - 45 - 15 - 15
    
    # ===== ПОГОДА =====
    draw.text((center_x, y_pos-35), "ПОГОДА В УКРАЇНІ", fill=BLUE, font=fonts['header'], anchor="mt")
    
    y_pos += 30
    
    weather = data['weather'].get('cities', [])
    for i, city in enumerate(weather[:5]):
        y = y_pos + i * 36
        name = city.get('name', '')
        temp = city.get('temp', '')
        condition = city.get('condition', '')
        
        # Извлекаем температуру (число)
        import re
        temp_match = re.search(r'(\d+\.?\d*)', temp)
        if temp_match:
            temp_clean = temp_match.group(1)
        else:
            temp_clean = "н/д"
        
        # ===== ИНДИВИДУАЛЬНЫЕ ШИФТЫ ДЛЯ КАЖДОГО ГОРОДА =====
        if name == "Київ":
            shift_name = -300
            shift_temp = -100
            shift_condition = 230
        elif name == "Одеса":
            shift_name = -290
            shift_temp = -100
            shift_condition = 230
        elif name == "Львів":
            shift_name = -295
            shift_temp = -100
            shift_condition = 230
        else:
            shift_name = -250
            shift_temp = -80
            shift_condition = 60
        
        # Название города
        draw.text((center_x + shift_name, y), f"{name}", fill=BLUE, font=fonts['big'], anchor="mt")
        
        # Температура
        draw.text((center_x + shift_temp, y), f"{temp_clean}°C", fill=BLUE, font=fonts['big'], anchor="mt")
        
        # Описание
        condition_clean = condition.replace('МІНДІЛІВА', 'МІНЛИВА').upper()
        draw.text((center_x + shift_condition, y), condition_clean, fill=BLUE, font=fonts['big'], anchor="mt")
    
    # ===== ПРОБЕЛ МЕЖДУ ПОГОДОЙ И ТОПЛИВОМ =====
    y_pos = y_pos + 5 * 36 + 15
    
    # ===== ТОПЛИВО =====
    y_pos = y_pos - 30
    
    shift_right = 150
    shift_title = 0
    
    draw.text((center_x + shift_title, y_pos-35), "ВАРТІСТЬ ПАЛЬНОГО", fill=BLUE, font=fonts['header'], anchor="mt")
    
    y_pos += 30
    
    # Получаем цены
    fuel_prices = get_fuel_prices_for_display()
    
    if not fuel_prices:
        fuel_prices = {
            "Київ": {"a95": "85.19", "dt": "85.31", "gas": "81.96"},
            "Одеса": {"a95": "85.00", "dt": "85.00", "gas": "81.00"},
            "Львів": {"a95": "85.00", "dt": "85.73", "gas": "81.00"}
        }
    
    # ===== ЗАГОЛОВКИ ТИПОВ ТОПЛИВА =====
    shift_fuel = -75
    
    draw.text((center_x - 200 + shift_right + shift_fuel, y_pos), "А-95", fill=BLUE, font=fonts['small'], anchor="mt")
    draw.text((center_x + 50 + shift_right + shift_fuel, y_pos), "ДТ", fill=BLUE, font=fonts['small'], anchor="mt")
    draw.text((center_x + 280 + shift_right + shift_fuel, y_pos), "Газ", fill=BLUE, font=fonts['small'], anchor="mt")
    y_pos += 25
    
    # ===== ДАННЫЕ ПО ГОРОДАМ =====
    kyiv_shift = 103
    odesa_shift = 112
    lviv_shift = 105
    
    for city_name in ["Київ", "Одеса", "Львів"]:
        if city_name in fuel_prices:
            city_x_offset = 0
            if city_name == "Київ":
                city_x_offset = kyiv_shift
            elif city_name == "Одеса":
                city_x_offset = odesa_shift
            elif city_name == "Львів":
                city_x_offset = lviv_shift
            
            draw.text((center_x - 625 + shift_right + city_x_offset, y_pos), city_name, fill=BLUE, font=fonts['big'], anchor="mt")
            
            a95 = fuel_prices[city_name].get('a95', '0')
            dt = fuel_prices[city_name].get('dt', '0')
            gas = fuel_prices[city_name].get('gas', '0')
            
            draw.text((center_x - 200 + shift_right + shift_fuel, y_pos), f"{a95} грн", fill=BLUE, font=fonts['big'], anchor="mt")
            draw.text((center_x + 50 + shift_right + shift_fuel, y_pos), f"{dt} грн", fill=BLUE, font=fonts['big'], anchor="mt")
            draw.text((center_x + 280 + shift_right + shift_fuel, y_pos), f"{gas} грн", fill=BLUE, font=fonts['big'], anchor="mt")
            
            y_pos += 42
    
    return y_pos
