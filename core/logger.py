import logging
import os
from datetime import datetime

# Создаем папку для логов, если её нет
if not os.path.exists("logs"):
    os.makedirs("logs")

def setup_logger():
    """Настройка профессионального логирования"""
    logger = logging.getLogger("RobloxMathBot")
    logger.setLevel(logging.DEBUG)

    # Формат записи: Дата Время - Тип (INFO/ERROR) - Сообщение
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Файл лога (создает новый файл каждый день)
    log_filename = f"logs/log_{datetime.now().strftime('%Y-%m-%d')}.txt"
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Вывод лога в консоль (терминал)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Создаем глобальный объект логгера для использования во всех файлах
log = setup_logger()