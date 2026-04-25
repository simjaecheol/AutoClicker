from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QColor, QPainter

class CoordinatePicker(QWidget):
    # Signal emitted when a coordinate is picked
    coordinate_picked = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        # Frameless, stay on top, and tool window (no taskbar icon)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True) # Track mouse without clicking
        
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Semi-transparent overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))
        
        # Draw current coordinates near cursor
        pos = self.mapFromGlobal(QCursor.pos())
        painter.setPen(Qt.white)
        painter.drawText(pos.x() + 15, pos.y() + 25, 
                         f"X: {QCursor.pos().x()}, Y: {QCursor.pos().y()}\nClick to pick (Esc to cancel)")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            global_pos = event.globalPos()
            self.coordinate_picked.emit(global_pos.x(), global_pos.y())
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def mouseMoveEvent(self, event):
        self.update()
