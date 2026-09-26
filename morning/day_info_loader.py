from datetime import datetime
from typing import Dict, Optional
from morning.day_info.names import NAMES_DB
from morning.day_info.events import EVENTS_DB
from morning.day_info.births import BIRTHS_DB
from utils.logger import get_logger

logger = get_logger(__name__)

def get_day_info(date: Optional[datetime] = None) -> Dict:
    """
    Возвращает информацию о дне из ручной базы данных
    """
    if date is None:
        date = datetime.now()
    
    key = date.strftime("%m-%d")
    
    name_day = NAMES_DB.get(key, "Дані відсутні")
    events = EVENTS_DB.get(key, ["Дані відсутні"])
    births = BIRTHS_DB.get(key, ["Дані відсутні"])
    
    return {
        "name_day": name_day,
        "church": get_church_holiday(key),
        "events": events,
        "born": births
    }

def get_church_holiday(key: str) -> str:
    """
    Возвращает церковный праздник для даты
    """
    church_holidays = {
        "01-07": "Різдво Христове",
        "01-14": "Обрізання Господнє",
        "01-19": "Богоявлення (Водохреща)",
        "02-15": "Стрітення Господнє",
        "04-07": "Благовіщення Пресвятої Богородиці",
        "06-28": "Рівноапостольного князя Володимира",
        "07-15": "Святої Ольги",
        "08-19": "Преображення Господнє",
        "08-28": "Успіння Пресвятої Богородиці",
        "09-08": "Різдво Пресвятої Богородиці",
        "09-14": "Воздвиження Чесного Хреста",
        "10-14": "Покрова Пресвятої Богородиці",
        "11-21": "Собор Архистратига Михаїла",
        "12-19": "Святителя Миколая",
        "12-25": "Різдво Христове",
        "09-04": "Ікона Божої Матері «Неопалима Купина»"
    }
    return church_holidays.get(key, "Дані відсутні")

def format_day_info(info: Dict) -> str:
    """Форматирует информацию о дне для отправки"""
    lines = []
    
    if info.get("name_day") and info["name_day"] != "Дані відсутні":
        lines.append(f"👼 Іменини: {info['name_day']}")
    
    if info.get("church") and info["church"] != "Дані відсутні":
        lines.append(f"🕊️ Церковне свято: {info['church']}")
    
    if info.get("events") and info["events"] != ["Дані відсутні"]:
        lines.append("")
        for event in info['events']:
            if event != "Дані відсутні":
                lines.append(f"📖 {event}")
    
    if info.get("born") and info["born"] != ["Дані відсутні"]:
        lines.append("")
        lines.append(f"🎂 Народилися: {', '.join(info['born'])}")
    
    return "\n".join(lines)

def get_today_info() -> str:
    """Возвращает отформатированную информацию о сегодняшнем дне"""
    info = get_day_info()
    return format_day_info(info)

if __name__ == "__main__":
    print("📅 Інформація про сьогоднішній день:")
    print("=" * 50)
    print(get_today_info())
    print("=" * 50)
