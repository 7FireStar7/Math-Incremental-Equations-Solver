import re
from core.logger import log

def parse_and_solve(text):
    if not text:
        return None
        
    log.info(f"Сырой текст OCR: '{text}'")
    
    # 1. Отсекаем всё, что после '=' или '?'
    # Если OCR увидел "180048 / 48 = ?", мы оставим только "180048 / 48"
    parts = re.split(r'[=?]', text)
    processing_text = parts[0]
    
    # 2. Ищем все числа
    all_nums = re.findall(r'\d+', processing_text)
    
    # Фильтруем мусор (нам нужны числа от 3 до 6 знаков)
    valid_nums = [n for n in all_nums if len(n) >= 3]

    if len(valid_nums) >= 2:
        n1 = valid_nums[0]
        n2 = valid_nums[1]
        
        # Правило: 3x3 = умножение, (4-6)x3 = деление
        if len(n1) == 3 and len(n2) == 3:
            op = "multiply"
        elif len(n1) >= 4 and len(n2) == 3:
            op = "divide"
        else:
            # Если не подпало под правила, ищем знак 'X' или '*'
            op = "multiply" if 'X' in processing_text.upper() or '*' in processing_text else "divide"
            
        log.info(f"Определено: {n1} {op} {n2}")
        return do_math(n1, n2, op)
    
    log.warning(f"Недостаточно данных в блоке: {processing_text}")
    return None

def do_math(n1, n2, op):
    try:
        v1, v2 = int(n1), int(n2)
        if op == "multiply":
            res = v1 * v2
        else:
            if v2 == 0: return None
            res = v1 / v2
        return round(res)
    except Exception as e:
        log.error(f"Ошибка расчёта: {e}")
        return None