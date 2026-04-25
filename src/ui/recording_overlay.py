from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont

class RecordingOverlay(QWidget):
    """A semi-transparent overlay that stays on top to indicate recording status."""
    def __init__(self):
        super().__init__()
        
        # Make it frameless, always on top, a tool window, and click-through
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setup_ui()
        
        # Blink timer for the recording indicator
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self._toggle_blink)
        self.is_blinking = False

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.label = QLabel("⏺ RECORDING")
        font = QFont("Arial", 12, QFont.Bold)
        self.label.setFont(font)
        self.label.setStyleSheet("color: red; background-color: rgba(0, 0, 0, 150); border-radius: 5px; padding: 5px;")
        self.label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.label)
        
        # Position it at top center of the primary screen
        self.adjustSize()
        # Note: Positioning will be handled when show() is called

    def show_recording(self):
        self.label.setText("⏺ RECORDING")
        self.label.setStyleSheet("color: red; background-color: rgba(0, 0, 0, 180); border-radius: 5px; padding: 5px;")
        self.blink_timer.start(500)
        self.show()
        self._center_top()

    def show_paused(self):
        self.blink_timer.stop()
        self.label.setText("⏸ PAUSED")
        self.label.setStyleSheet("color: yellow; background-color: rgba(0, 0, 0, 180); border-radius: 5px; padding: 5px;")
        self.show()
        self._center_top()

    def hide_overlay(self):
        self.blink_timer.stop()
        self.hide()

    def _toggle_blink(self):
        self.is_blinking = not self.is_blinking
        if self.is_blinking:
            self.label.setStyleSheet("color: transparent; background-color: rgba(0, 0, 0, 180); border-radius: 5px; padding: 5px;")
        else:
            self.label.setStyleSheet("color: red; background-color: rgba(0, 0, 0, 180); border-radius: 5px; padding: 5px;")

    def _center_top(self):
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = 10 # 10 pixels from the top
        self.move(x, y)
