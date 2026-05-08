import easyocr
import numpy as np
from core.logger import log

class OCREngine:
    def __init__(self):
        log.info("Инициализация EasyOCR...")
        # Используем английский, так как нам нужны только цифры
        self.reader = easyocr.Reader(['en'], gpu=False) 
        log.info("EasyOCR успешно загружен.")

    def read_text(self, image):
        try:
            if image is None:
                return []
            
            log.info("Начинаю сканирование изображения нейросетью...")
            # detail=1 возвращает координаты, текст и уверенность
            results = self.reader.readtext(image, detail=1)
            log.info(f"Сканирование завершено. Найдено объектов: {len(results)}")
            return results
        except Exception as e:
            log.error(f"Ошибка внутри EasyOCR: {e}")
            return []

ocr_tool = OCREngine()