import json
import os

# Путь к файлу настроек
CONFIG_FILE = "config.json"

# Начальные настройки по умолчанию
DEFAULT_CONFIG = {
    "ocr_area": [100, 100, 500, 500],  # [x, y, width, height]
    "confidence_threshold": 0.6,      # Насколько OCR должен быть уверен (0.0 - 1.0)
    "click_delay": 1.5,               # Задержка перед кликом (секунды)
    "debug_mode": True,               # Сохранять ли скриншоты ошибок
    "hotkeys": {
        "pause": "f9",
        "stop": "f10"
    }
}

def load_config():
    """Загружает конфиг из файла или создает новый с дефолтными значениями"""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config_data):
    """Сохраняет переданные данные в config.json"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)