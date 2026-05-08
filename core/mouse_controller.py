import time
import random
import ctypes
import re
import win32api
from core.logger import log

# Настройка структур для прямого обращения к Windows API
PUL = ctypes.POINTER(ctypes.c_ulong)
class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("mi", MouseInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Константы для SendInput
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000

def send_input_move(x, y):
    """Отправка координат через SendInput в абсолютных единицах"""
    nx = int(x * 65535 / win32api.GetSystemMetrics(0))
    ny = int(y * 65535 / win32api.GetSystemMetrics(1))
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.mi = MouseInput(nx, ny, 0, MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def send_input_click(down=True):
    """Выполнение клика через SendInput"""
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    flag = MOUSEEVENTF_LEFTDOWN if down else MOUSEEVENTF_LEFTUP
    ii_.mi = MouseInput(0, 0, 0, flag, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

class MouseController:
    def click_at(self, x, y):
        try:
            tx, ty = int(x), int(y)
            log.info(f"SendInput: наведение на ({tx}, {ty})")

            # 1. Плавная имитация аппаратного перемещения сенсора
            steps = 15
            start_x, start_y = win32api.GetCursorPos()
            for i in range(1, steps + 1):
                curr_x = start_x + int((tx - start_x) * i / steps)
                curr_y = start_y + int((ty - start_y) * i / steps)
                send_input_move(curr_x, curr_y)
                time.sleep(0.01)

            # 2. Небольшая задержка перед нажатием для стабилизации (как у человека)
            time.sleep(0.1)

            # 3. ОДИНОЧНЫЙ КЛИК (как ты просил)
            send_input_click(True)  # Зажать
            time.sleep(0.15)        # Удержание
            send_input_click(False) # Отпустить
            
            log.info("Клик через SendInput завершен успешно.")

        except Exception as e:
            log.error(f"Ошибка SendInput: {e}")

def find_best_match(ocr_results, target_value):
    target_str = str(target_value)
    if not ocr_results: return None, 0
    for res in ocr_results:
        if len(res) < 2: continue
        bbox, text = res[0], str(res[1])
        clean_text = re.sub(r'\D', '', text)
        if target_str == clean_text or target_str in clean_text:
            cx = int((bbox[0][0] + bbox[2][0]) / 2)
            cy = int((bbox[0][1] + bbox[2][1]) / 2)
            return (cx, cy), 1.0
    return None, 0

mouse = MouseController()