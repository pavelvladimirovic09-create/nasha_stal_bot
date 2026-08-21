import requests
from typing import Dict, Optional

COORDS = {
    "kyiv": {"lat": 50.4501, "lon": 30.5234},
    "odesa": {"lat": 46.4825, "lon": 30.7233},
    "lviv": {"lat": 49.8397, "lon": 24.0297}
}

WEATHER_CODES = {
    0: "ясно", 1: "ясно", 2: "мінлива хмарність",
    3: "хмарно", 45: "туман", 51: "морось",
    61: "дощ", 63: "дощ", 71: "сніг", 80: "злива"
}

def get_weather(city: str) -> Optional[Dict]:
    try:
        if city not in COORDS:
            return None
        lat = COORDS[city]["lat"]
        lon = COORDS[city]["lon"]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=Europe/Kiev"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        weather = data.get('current_weather', {})
        code = weather.get('weathercode', 0)
        return {
            "city": city,
            "temp": f"{weather.get('temperature', 'н/д')}°C",
            "description": WEATHER_CODES.get(code, "ясно")
        }
    except Exception:
        return None

def get_all_weather():
    result = {}
    for city_key in COORDS:
        data = get_weather(city_key)
        if data:
            result[city_key] = data
    return result
