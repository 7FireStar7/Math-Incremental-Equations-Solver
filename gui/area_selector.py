import sys
from PyQt6.QtWidgets import QRubberBand, QWidget, QApplication
from PyQt6.QtCore import QPoint, QRect, QSize, Qt, pyqtSignal

class AreaSelector(QWidget):
    area_selected = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setWindowOpacity(0.3)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.origin = QPoint()
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        if not self.origin.isNull():
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            rect = self.rubber_band.geometry()
            area = [rect.x(), rect.y(), rect.width(), rect.height()]
            self.area_selected.emit(area)
            self.rubber_band.hide()
            self.close() # ПРИНУДИТЕЛЬНО ЗАКРЫВАЕМ
            QApplication.processEvents() # Ждем, пока Windows уберет окно