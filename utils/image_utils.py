import cv2
import numpy as np

def preprocess_for_ocr(img):
    """Готовит картинку для идеального распознавания"""
    if img is None:
        return None
        
    # 1. Переводим в оттенки серого
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Увеличиваем картинку в 2 раза (OCR лучше работает с крупным текстом)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # 3. Убираем шумы
    distorted = cv2.fastNlMeansDenoising(gray, h=10)
    
    # 4. Бинаризация (делаем текст черным, а фон белым)
    # Используем адаптивный порог, так как освещение в Roblox меняется
    thresh = cv2.threshold(distorted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    return thresh