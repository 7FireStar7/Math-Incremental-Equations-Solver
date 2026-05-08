import sys
from utils.hotkeys import setup_global_hotkeys, cleanup_hotkeys
from PyQt6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QWidget, 
                             QLabel, QGroupBox, QCheckBox)
from PyQt6.QtCore import QThread, pyqtSlot
from gui.area_selector import AreaSelector
from gui.workers import SolverWorker
from utils.config_manager import load_config, save_config
from core.logger import log

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Math-Incremental-Equations-Solver")
        self.setFixedSize(400, 450)
        self.config = load_config()
        self.thread = None
        self.worker = None
        
        self.init_ui()

        setup_global_hotkeys(self.toggle_pause, self.stop_solver)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Кнопки управления
        self.btn_select = QPushButton("1. Выбрать область")
        self.btn_select.clicked.connect(self.open_area_selector)
        
        self.btn_start = QPushButton("2. START")
        self.btn_start.clicked.connect(self.start_solver)
        self.btn_start.setStyleSheet("background-color: #2ecc71; font-weight: bold;")

        self.btn_stop = QPushButton("STOP")
        self.btn_stop.clicked.connect(self.stop_solver)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("background-color: #e74c3c;")

        # Информационная панель
        stats_group = QGroupBox("Работа бота")
        stats_layout = QVBoxLayout()
        self.lbl_status = QLabel("Статус: Готов")
        self.lbl_res = QLabel("Пример: ---")
        self.lbl_solved = QLabel("Решено: 0")
        stats_layout.addWidget(self.lbl_status)
        stats_layout.addWidget(self.lbl_res)
        stats_layout.addWidget(self.lbl_solved)
        stats_group.setLayout(stats_layout)

        layout.addWidget(self.btn_select)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        layout.addWidget(stats_group)
        layout.addWidget(QLabel("F6: Пауза | F7: Стоп (Экстренно)"))

    def open_area_selector(self):
        self.selector = AreaSelector()
        self.selector.area_selected.connect(self.save_area)
        self.selector.show()

    def save_area(self, area):
        self.config["ocr_area"] = area
        save_config(self.config)
        self.lbl_status.setText("Статус: Область сохранена")

    def start_solver(self):
        self.thread = QThread()
        self.worker = SolverWorker(self.config)
        self.worker.moveToThread(self.thread)

        # Соединяем сигналы
        self.thread.started.connect(self.worker.run)
        self.worker.status_signal.connect(self.update_status)
        self.worker.stats_signal.connect(self.update_stats)
        self.worker.finished.connect(self.thread.quit)
        
        self.thread.start()
        
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        log.info("Бот запущен пользователем")

    def stop_solver(self):
        if self.worker:
            log.info("Запрос на остановку бота...")
            self.worker.is_running = False
            # Ждем завершения потока до 2 секунд
            if not self.worker.wait(2000):
                log.warning("Поток не ответил, принудительное завершение.")
                self.worker.terminate()
                self.worker.wait()
            
            self.worker = None
            if self.thread:
                self.thread.quit()
                self.thread.wait()
                self.thread = None

        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.lbl_status.setText("Статус: Остановлен")

    @pyqtSlot(str)
    def update_status(self, text):
        self.lbl_status.setText(text)

    @pyqtSlot(dict)
    def update_stats(self, data):
        self.lbl_res.setText(f"Пример: {data['equation']} = {data['answer']}")
        self.lbl_solved.setText(f"Решено: {data['solved']}")

    def toggle_pause(self):
        if self.worker:
            self.worker.is_paused = not self.worker.is_paused
            status = "ПАУЗА" if self.worker.is_paused else "РАБОТАЕТ"
            self.lbl_status.setText(f"Статус: {status}")
            log.info(f"Бот переключен в режим: {status}")