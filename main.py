import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from core.logger import log

def main():
    try:
        app = QApplication(sys.argv)
        
        # Устанавливаем стиль (необязательно, но так приятнее)
        app.setStyle("Fusion")
        
        window = MainWindow()
        window.show()
        
        log.info("Приложение запущено")
        sys.exit(app.exec())
    except Exception as e:
        log.critical(f"Критическая ошибка при запуске: {e}")

if __name__ == "__main__":
    main()