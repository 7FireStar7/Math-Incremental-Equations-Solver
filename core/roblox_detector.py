import pywintypes
import win32gui
from core.logger import log

def is_roblox_active():
    """Проверяет, является ли окно Roblox активным в данный момент"""
    try:
        # Получаем заголовок активного окна
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)
        
        # Обычно окно называется 'Roblox'
        if "Roblox" in title:
            return True
        return False
    except Exception as e:
        log.error(f"Ошибка при проверке окна: {e}")
        return False