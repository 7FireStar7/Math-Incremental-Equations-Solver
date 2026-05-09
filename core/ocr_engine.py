import easyocr
import torch
from core.logger import log

class OCREngine:
    def __init__(self):
        # Проверяем твою видеокарту через установленный PyTorch
        self.use_gpu = torch.cuda.is_available()
        
        if self.use_gpu:
            device = torch.cuda.get_device_name(0)
            log.info(f"🚀 GPU МОЩНОСТЬ АКТИВИРОВАНА: {device}")
        else:
            log.warning("⚠️ GPU не найден. Проверь драйверы NVIDIA.")
            
        # Инициализация нейросети
        self.reader = easyocr.Reader(['en'], gpu=self.use_gpu)

    def read_text(self, img):
        # ВАЖНО: Метод называется readtext без подчеркивания!
        return self.reader.readtext(img, detail=1)

ocr_tool = OCREngine()