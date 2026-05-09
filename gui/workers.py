import time
import cv2
import numpy as np
import mss
from PyQt6.QtCore import QThread, pyqtSignal
from core.screen_capture import capture_region
from core.equation_parser import parse_and_solve
from core.ocr_engine import ocr_tool
from core.mouse_controller import mouse, find_best_match
from core.logger import log

class SolverWorker(QThread):
    stats_signal = pyqtSignal(str, int)
    status_signal = pyqtSignal(str) # Сигнал для обновления статуса в UI

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.is_running = True
        self.is_paused = False
        self.solved_count = 0
        self.last_eq = ""
        self.fail_count = 0

    def run(self):
        # --- ТВОЕ ОБНОВЛЕНИЕ: ЗАДЕРЖКА ПЕРЕД ПЕРВЫМ СТАРТОМ ---
        log.info("⏳ Подготовка к запуску... У вас есть 5 секунд.")
        # Оповещаем интерфейс (если нужно вывести обратный отсчет в консоль или лог)
        for i in range(5, 0, -1):
            if not self.is_running: return # Если нажали STOP во время ожидания
            log.info(f"Запуск через {i}...")
            time.sleep(1)
        
        log.info("🚀 ЦИКЛ ЗАПУЩЕН!")
        # -----------------------------------------------------

        with mss.mss() as sct:
            main_mon = sct.monitors[1]
            while self.is_running:
                if self.is_paused:
                    time.sleep(0.3)
                    continue

                try:
                    area = self.config.get('ocr_area')
                    if not area: continue

                    img = capture_region(area)
                    if img is None: continue
                    
                    # Используем исправленный метод read_text (внутри которого readtext)
                    ocr_res = ocr_tool.read_text(img)
                    full_text = " ".join([str(r[1]) for r in ocr_res])
                    result = parse_and_solve(full_text)

                    if result is not None and self.is_running:
                        if full_text == self.last_eq:
                            self.fail_count += 1
                        else:
                            self.last_eq = full_text
                            self.fail_count = 0

                        sct_img = sct.grab(main_mon)
                        frame = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
                        all_ocr = ocr_tool.read_text(frame)
                        
                        filtered = []
                        for res in all_ocr:
                            box = res[0]
                            cx, cy = (box[0][0]+box[2][0])/2, (box[0][1]+box[2][1])/2
                            if not (area[0] < cx < area[0]+area[2] and area[1] < cy < area[1]+area[3]):
                                filtered.append(res)

                        btn_coords, _ = find_best_match(filtered, result)

                        if (not btn_coords or self.fail_count >= 3) and filtered:
                            log.warning("🔄 Анти-ступор: Пропуск примера")
                            box = filtered[0][0]
                            btn_coords = ((box[0][0]+box[2][0])/2, (box[0][1]+box[2][1])/2)

                        if btn_coords and self.is_running:
                            mouse.click_at(main_mon['left'] + btn_coords[0], main_mon['top'] + btn_coords[1])
                            self.solved_count += 1
                            self.stats_signal.emit(full_text, self.solved_count)
                            
                            # Скорость цикла
                            time.sleep(0.65)
                            
                except Exception as e:
                    log.error(f"Ошибка цикла: {e}")
                time.sleep(0.05)

    def stop(self):
        self.is_running = False
        self.wait()