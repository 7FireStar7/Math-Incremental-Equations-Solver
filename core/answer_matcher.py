import re
from core.logger import log

def find_best_match(ocr_results, target_answer):
    """
    ocr_results: список кортежей от EasyOCR [(bbox, text, prob), ...]
    target_answer: число (результат решения примера)
    
    Возвращает: координаты (x, y) центра текста, который совпал с ответом.
    """
    target_str = str(target_answer)
    
    for (bbox, text, prob) in ocr_results:
        # Очищаем текст от мусора (оставляем только цифры)
        clean_text = re.sub(r'[^0-9]', '', text)
        
        if clean_text == target_str:
            # bbox - это 4 точки угла [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
            # Считаем центр
            x_center = int((bbox[0][0] + bbox[2][0]) / 2)
            y_center = int((bbox[0][1] + bbox[2][1]) / 2)
            
            log.info(f"Ответ найден: '{text}' на позиции ({x_center}, {y_center}) с уверенностью {prob:.2f}")
            return (x_center, y_center), prob
            
    log.warning(f"Правильный ответ {target_answer} не найден среди распознанных вариантов.")
    return None, 0