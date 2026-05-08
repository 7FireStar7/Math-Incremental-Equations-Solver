import keyboard
from core.logger import log

def setup_global_hotkeys(on_pause_callback, on_stop_callback):
    """
    Регистрирует системные горячие клавиши.
    on_pause_callback: функция, которая сработает при нажатии F6
    on_stop_callback: функция, которая сработает при нажатии F7
    """
    try:
        # Убираем все старые горячие клавиши, чтобы не было дублей
        keyboard.unhook_all()
        
        # F6 - Пауза/Возобновление
        keyboard.add_hotkey('f6', on_pause_callback)
        # F7 - Полная остановка (Emergency Stop)
        keyboard.add_hotkey('f7', on_stop_callback)
        
        log.info("Горячие клавиши настроены: F6 (Пауза), F7 (Стоп)")
    except Exception as e:
        log.error(f"Ошибка при настройке горячих клавиш: {e}")

def cleanup_hotkeys():
    keyboard.unhook_all()