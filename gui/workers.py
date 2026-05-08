import time
import cv2
import numpy as np
import mss
from PyQt6.QtCore import QThread, pyqtSignal
from core.screen_capture import capture_region, save_debug_image
from core.equation_parser import parse_and_solve
from core.ocr_engine import ocr_tool
from core.mouse_controller import mouse, find_best_match
from core.logger import log

class SolverWorker(QThread):
    finished = pyqtSignal()
    status_signal = pyqtSignal(str)
    stats_signal = pyqtSignal(dict)

    def __init__(self, region_data):
        super().__init__()
        self.region_data = region_data
        self.is_running = True
        self.is_paused = False
        self.solved_count = 0

    def run(self):
        log.info("Воркер запущен в режиме стабильного цикла.")
        with mss.mss() as sct:
            main_mon = sct.monitors[1]
            while self.is_running:
                if self.is_paused:
                    time.sleep(0.5)
                    continue
                try:
                    if not self.is_running: break
                    
                    area = self.region_data.get('ocr_area') if isinstance(self.region_data, dict) else self.region_data
                    img = capture_region(area)
                    if img is None: continue
                    
                    from utils.image_utils import preprocess_for_ocr
                    ocr_res = ocr_tool.read_text(preprocess_for_ocr(img))
                    full_text = " ".join([str(r[1]) for r in ocr_res if len(r) > 1])
                    result = parse_and_solve(full_text)

                    if result is not None and self.is_running:
                        sct_img = sct.grab(main_mon)
                        frame = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
                        
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        processed_frame = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
                        save_debug_image(processed_frame, "full_screen_search")
                        
                        full_ocr = ocr_tool.read_text(processed_frame)
                        btn_coords, conf = find_best_match(full_ocr, result)

                        if btn_coords and self.is_running:
                            final_x = main_mon['left'] + btn_coords[0]
                            final_y = main_mon['top'] + btn_coords[1]
                            
                            mouse.click_at(final_x, final_y)
                            
                            self.solved_count += 1
                            self.stats_signal.emit({"equation": full_text, "answer": str(result), "solved": str(self.solved_count)})
                            
                            # Умная задержка 1.7с с проверкой флага остановки
                            for _ in range(17):
                                if not self.is_running: break
                                time.sleep(0.1)
                except Exception as e:
                    log.error(f"Ошибка воркера: {e}")
                time.sleep(0.1)
        log.info("Поток воркера успешно остановлен.")

    def stop(self):
        self.is_running = False
        self.wait()