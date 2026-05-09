import sys
from PyQt6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QFrame, QApplication, QGraphicsDropShadowEffect, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSlot, QThread
from PyQt6.QtGui import QColor, QFont
from gui.area_selector import AreaSelector
from gui.workers import SolverWorker
from utils.config_manager import load_config, save_config
from utils.hotkeys import setup_global_hotkeys

# --- ГЛОБАЛЬНЫЙ СТИЛЬ ОСТАВЛЕН БЕЗ ИЗМЕНЕНИЙ ---
STYLE = """
QMainWindow { background-color: #0d0d12; }
QLabel { color: #e0e0e0; font-family: 'Segoe UI', sans-serif; font-size: 11pt; }

QPushButton {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a1a26, stop:1 #12121a);
    color: #e0e0e0;
    border: 1px solid #333340;
    border-radius: 12px;
    font-size: 12pt;
    font-weight: bold;
    padding: 15px;
}
QPushButton:hover { background-color: #252533; }

QPushButton#selectAreaBtn {
    color: #ffbf00;
    border: 2px solid #333340;
}

QPushButton#startBtn { color: #00ff00; background-color: #1a1a26; }
QPushButton#stopBtn { color: #ff3131; background-color: #1a1a26; }

QFrame#infoCard {
    background-color: #1a1a26;
    border: 1px solid #333340;
    border-radius: 18px;
}

QFrame#eqContainer {
    background-color: #0a0a10;
    border: 1px solid #333340;
    border-radius: 12px;
}

QLabel#eqDisplay {
    color: #e0e0e0;
    font-family: 'Consolas';
    font-size: 26pt;
    font-weight: bold;
}

QLabel#statusReady { color: #a4e404; }
QLabel#solvedCount { color: #00e5ff; }
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Math Incremental Equations Solver v0.8")
        self.setFixedSize(500, 620)
        self.config = load_config()
        self.worker = None
        self.thread = None
        
        self.init_ui()
        self.setStyleSheet(STYLE)
        self._setup_neon_glow()
        setup_global_hotkeys(self.toggle_pause, self.on_stop)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        self.layout = QVBoxLayout(central)
        self.layout.setContentsMargins(40, 30, 40, 20)
        self.layout.setSpacing(15)

        header_row = QHBoxLayout()
        sig_logo = QLabel("Σ")
        sig_logo.setStyleSheet("color: #00e5ff; font-size: 22pt; font-weight: 900;")
        main_title = QLabel("MATH SOLVER")
        main_title.setStyleSheet("font-size: 20pt; font-weight: 900;")
        header_row.addWidget(sig_logo)
        header_row.addWidget(main_title)
        header_row.addStretch()
        self.layout.addLayout(header_row)

        self.card = QFrame()
        self.card.setObjectName("infoCard")
        self.card.setFixedHeight(180)
        card_layout = QVBoxLayout(self.card)

        self.status_lbl = QLabel("Status: Ready")
        self.status_lbl.setObjectName("statusReady")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.status_lbl)

        self.eq_container = QFrame()
        self.eq_container.setObjectName("eqContainer")
        eq_layout = QVBoxLayout(self.eq_container)
        self.eq_lbl = QLabel("EXAMPLE: 12345 / 312")
        self.eq_lbl.setObjectName("eqDisplay")
        self.eq_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        eq_layout.addWidget(self.eq_lbl)
        card_layout.addWidget(self.eq_container)

        self.count_lbl = QLabel("SOLVED: 0")
        self.count_lbl.setObjectName("solvedCount")
        self.count_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.count_lbl)
        
        self.layout.addWidget(self.card)
        self.layout.addSpacing(10)

        self.btn_area = QPushButton("SELECT AREA")
        self.btn_area.setObjectName("selectAreaBtn")
        self.btn_area.setFixedHeight(60)
        self.btn_area.clicked.connect(self.on_select_area)
        self.layout.addWidget(self.btn_area)

        row_controls = QHBoxLayout()
        self.btn_start = QPushButton("START")
        self.btn_start.setObjectName("startBtn")
        self.btn_start.setFixedHeight(70)
        self.btn_start.clicked.connect(self.on_start)
        
        self.btn_stop = QPushButton("STOP")
        self.btn_stop.setObjectName("stopBtn")
        self.btn_stop.setFixedHeight(70)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.on_stop)
        
        row_controls.addWidget(self.btn_start)
        row_controls.addWidget(self.btn_stop)
        self.layout.addLayout(row_controls)

        footer = QLabel("F6: PAUSE | F7: STOP (EMERGENCY)")
        footer.setStyleSheet("color: #555566; font-size: 9pt;")
        self.layout.addWidget(footer, alignment=Qt.AlignmentFlag.AlignCenter)

    def _setup_neon_glow(self):
        self.start_glow = QGraphicsDropShadowEffect()
        self.start_glow.setBlurRadius(25)
        self.start_glow.setColor(QColor(0, 255, 0, 150))
        self.start_glow.setOffset(0, 0)
        self.btn_start.setGraphicsEffect(self.start_glow)

        self.stop_glow = QGraphicsDropShadowEffect()
        self.stop_glow.setBlurRadius(25)
        self.stop_glow.setColor(QColor(255, 49, 49, 150))
        self.stop_glow.setOffset(0, 0)
        self.btn_stop.setGraphicsEffect(self.stop_glow)

    @pyqtSlot()
    def on_start(self):
        if not self.worker:
            self.thread = QThread()
            self.worker = SolverWorker(self.config)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.stats_signal.connect(self.update_ui)
            # --- ПОДКЛЮЧЕНИЕ СИГНАЛА СТАТУСА ---
            self.worker.status_signal.connect(self.status_lbl.setText)
            self.thread.start()
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            # Статус теперь обновляется воркером

    @pyqtSlot()
    def on_stop(self):
        if self.worker:
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
            self.worker = None
            self.thread = None
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.status_lbl.setText("Status: Stopped")

    def on_select_area(self):
        self.selector = AreaSelector()
        self.selector.area_selected.connect(self.save_area)
        self.selector.show()

    def save_area(self, area):
        self.config["ocr_area"] = area
        save_config(self.config)
        self.status_lbl.setText("Status: Ready")

    @pyqtSlot(str, int)
    def update_ui(self, eq, count):
        self.eq_lbl.setText(eq)
        self.count_lbl.setText(f"SOLVED: {count}")

    def toggle_pause(self):
        if self.worker:
            self.worker.is_paused = not self.worker.is_paused
            self.status_lbl.setText("Status: Paused" if self.worker.is_paused else "Status: Active")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())