from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel, 
                             QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPixmap
import time
import os
from models.raw_event import RawEvent
from hotkey.global_hotkey_manager import GlobalHotkeyManager
from utils.path_helper import get_resource_path

class RecordingToolbar(QWidget):
    # Signal to request main window to minimize when recording starts
    request_minimize = pyqtSignal()
    # Signal to request main window to restore when recording stops
    request_restore = pyqtSignal()

    def __init__(self, coordinator, hotkey_manager: GlobalHotkeyManager, overlay, parent=None):
        super().__init__(parent)
        self.coordinator = coordinator
        self.hotkey_manager = hotkey_manager
        self.overlay = overlay
        
        self.event_count = 0
        self.start_time = 0
        self.paused_time = 0
        self.total_paused_duration = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer_display)
        
        self.setup_ui()
        self.setup_signals()
        self.setup_hotkeys()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo
        self.lbl_logo = QLabel()
        logo_path = get_resource_path(os.path.join("resources", "icons", "logo.png"))
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_logo.setPixmap(pixmap)
        
        layout.addWidget(self.lbl_logo)
        
        self.group = QGroupBox("RPA Recording")
        group_layout = QHBoxLayout(self.group)
        
        # Buttons
        self.btn_record = QPushButton("⏺ Record")
        self.btn_record.setStyleSheet("color: red; font-weight: bold;")
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_stop = QPushButton("⏹ Stop")
        
        self.btn_record.clicked.connect(self._on_record_clicked)
        self.btn_pause.clicked.connect(self._on_pause_clicked)
        self.btn_stop.clicked.connect(self._on_stop_clicked)
        
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        
        group_layout.addWidget(self.btn_record)
        group_layout.addWidget(self.btn_pause)
        group_layout.addWidget(self.btn_stop)
        
        # Info Displays
        self.lbl_events = QLabel("Events: 0")
        self.lbl_time = QLabel("00:00")
        self.lbl_hotkey = QLabel("  (Hotkey: Ctrl+Shift+R to Stop)")
        self.lbl_hotkey.setStyleSheet("color: gray; font-size: 10px;")
        
        group_layout.addWidget(self.lbl_events)
        group_layout.addWidget(self.lbl_time)
        group_layout.addWidget(self.lbl_hotkey)
        
        group_layout.addStretch()
        layout.addWidget(self.group)

    def setup_signals(self):
        self.coordinator.recording_event_captured.connect(self._on_event_captured)

    def setup_hotkeys(self):
        # Note: PyQt signals must be used if hotkey callbacks update UI
        self.hotkey_manager.register({
            '<ctrl>+<shift>+r': self._toggle_recording,
            '<ctrl>+<shift>+p': self._toggle_pause
        })

    def _toggle_recording(self):
        # This is called from the pynput listener thread.
        # We use QMetaObject.invokeMethod to safely call UI methods on the main thread.
        from PyQt5.QtCore import QMetaObject, Qt
        if self.coordinator.is_active():
            QMetaObject.invokeMethod(self, "_on_stop_clicked", Qt.QueuedConnection)
        else:
            QMetaObject.invokeMethod(self, "_on_record_clicked", Qt.QueuedConnection)

    def _toggle_pause(self):
        from PyQt5.QtCore import QMetaObject, Qt
        QMetaObject.invokeMethod(self, "_on_pause_clicked", Qt.QueuedConnection)

    @pyqtSlot()
    def _on_record_clicked(self):
        if self.coordinator.is_active():
            return
            
        reply = QMessageBox.question(
            self, "Start Recording", 
            "Recording will start and the window will minimize.\nPress Ctrl+Shift+R to stop.\n\nStart now?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.event_count = 0
            self.total_paused_duration = 0
            self.start_time = time.time()
            self.lbl_events.setText("Events: 0")
            self._update_timer_display()
            
            self.btn_record.setEnabled(False)
            self.btn_pause.setEnabled(True)
            self.btn_stop.setEnabled(True)
            
            self.timer.start(1000)
            self.request_minimize.emit()
            self.overlay.show_recording()
            
            self.coordinator.start_recording()

    @pyqtSlot()
    def _on_pause_clicked(self):
        if not self.coordinator.is_active():
            return
            
        if self.btn_pause.text() == "⏸ Pause":
            self.coordinator.pause_recording()
            self.btn_pause.setText("▶ Resume")
            self.overlay.show_paused()
            self.paused_time = time.time()
        else:
            self.coordinator.resume_recording()
            self.btn_pause.setText("⏸ Pause")
            self.overlay.show_recording()
            if self.paused_time > 0:
                self.total_paused_duration += (time.time() - self.paused_time)
                self.paused_time = 0

    @pyqtSlot()
    def _on_stop_clicked(self):
        if not self.coordinator.is_active():
            return
            
        self.coordinator.stop_recording() # This emits recording_completed with the new Flow
        self.timer.stop()
        self.overlay.hide_overlay()
        self.request_restore.emit()
        
        self.btn_record.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_pause.setText("⏸ Pause")

    @pyqtSlot(object)
    def _on_event_captured(self, event: RawEvent):
        self.event_count += 1
        self.lbl_events.setText(f"Events: {self.event_count}")

    def _update_timer_display(self):
        if self.coordinator.is_recording() and self.btn_pause.text() == "⏸ Pause":
            elapsed = int(time.time() - self.start_time - self.total_paused_duration)
            mins, secs = divmod(elapsed, 60)
            self.lbl_time.setText(f"{mins:02d}:{secs:02d}")
