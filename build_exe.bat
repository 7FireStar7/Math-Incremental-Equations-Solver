@echo off
echo [BUILD] Начинаю сборку EXE...
venv\Scripts\python -m pip install pyinstaller
venv\Scripts\pyinstaller --noconfirm --onefile --windowed --name "RobloxMathBot" --collect-all easyocr --collect-all torch --add-data "config.json;." main.py
echo [BUILD] Сборка завершена! Проверь папку dist.
pause