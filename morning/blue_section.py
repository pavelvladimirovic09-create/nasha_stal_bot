from PIL import Image, ImageDraw, ImageFont

def draw_blue_section(draw, center_x, fonts, data):
    """
    Рисует всё на синем фоне (желтым текстом)
    ТОЛЬКО КУРСЫ ВАЛЮТ НАЦБАНК! Черный рынок УДАЛЕН!
    """
    YELLOW = (255, 215, 0)
    
    # ДАТА
    y_pos = 35
    draw.text((center_x, y_pos), data['date'], fill=YELLOW, font=fonts['title'], anchor="mt")
    y_pos += 50
    
    # ДЕНЬ НЕДЕЛИ - с маленькой
    draw.text((center_x, y_pos), data['day'].lower(), fill=YELLOW, font=fonts['text'], anchor="mt")
    y_pos += 50
    
    # ДЕНЬ ВОЙНЫ - с маленькой
    draw.text((center_x, y_pos), data['war'].lower(), fill=YELLOW, font=fonts['text'], anchor="mt")
    y_pos += 55
    
    # КУРС ВАЛЮТ - с маленькой
    try:
        font_currency = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except:
        font_currency = fonts['medium']
    
    draw.text((center_x, y_pos), "Курс валют", fill=YELLOW, font=font_currency, anchor="mt")
    y_pos += 80
    
    # ===== НАЦБАНК И ВЕСЬ ТЕКСТ ПОД НИМ ПОДНЯТ НА 15 ПИКСЕЛЕЙ =====
    y_pos = y_pos - 15  # Поднимаем на 1 единицу
    
    # НАЦБАНК
    try:
        font_nbu = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    except:
        font_nbu = fonts['subheader']
    
    draw.text((center_x, y_pos), "НАЦБАНК", fill=YELLOW, font=font_nbu, anchor="mt")
    y_pos += 35
    
    # ПОДПИСИ "Покупка" и "Продаж"
    spacing = 150
    draw.text((center_x - spacing, y_pos), "Покупка", fill=YELLOW, font=fonts['tiny'], anchor="mt")
    draw.text((center_x + spacing, y_pos), "Продаж", fill=YELLOW, font=fonts['tiny'], anchor="mt")
    
    y_pos += 25
    
    # КУРСЫ ВАЛЮТ НАЦБАНК
    currencies = data['currency'].get('currencies', [])
    name_spacing = 100
    
    for i in range(3):
        y = y_pos + i * 42
        
        if i < len(currencies):
            name = currencies[i].get('name', '')
            buy = currencies[i].get('buy', '')
            sell = currencies[i].get('sell', '')
            
            draw.text((center_x - spacing - name_spacing, y), name, fill=YELLOW, font=fonts['big'], anchor="mt")
            draw.text((center_x - spacing, y), buy, fill=YELLOW, font=fonts['big'], anchor="mt")
            draw.text((center_x + spacing, y), sell, fill=YELLOW, font=fonts['big'], anchor="mt")
    
    y_pos = y_pos + 3 * 42 + 90
    
    return y_pos
