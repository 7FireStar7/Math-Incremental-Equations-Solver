import pyautogui
import numpy as np
import cv2
import os
from core.logger import log

def capture_region(region):
    """
    Захватывает область экрана. 
    Поддерживает как список [x, y, w, h], так и словарь с ключом 'ocr_area'.
    """
    try:
        # Если случайно прилетел словарь с конфигом, достаем из него нужный список
        if isinstance(region, dict):
            region = region.get('ocr_area', [0, 0, 100, 100])
        
        # Проверка на корректность координат
        if not isinstance(region, (list, tuple)) or len(region) < 4:
            log.error(f"Некорректный формат региона: {region}")
            return None

        # Преобразование в целые числа и защита от выхода за границы (0,0)
        left = max(0, int(region[0]))
        top = max(0, int(region[1]))
        width = int(region[2])
        height = int(region[3])

        # Захват скриншота
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        
        # Конвертация для OpenCV
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return img
    except Exception as e:
        log.error(f"Ошибка в capture_region: {e}")
        return None

def save_debug_image(img, name):
    """Сохраняет изображение для отладки в папку debug."""
    if img is None:
        return
    if not os.path.exists("debug"):
        os.makedirs("debug")
    cv2.imwrite(f"debug/{name}.png", img)