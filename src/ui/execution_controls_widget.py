from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QProgressBar, QLabel, QSpinBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSlot
from engine.flow_engine import EngineState

class ExecutionControlsWidget(QWidget):
    def __init__(self, coordinator, parent=None):
        super().__init__(parent)
        self.coordinator = coordinator
        self.current_flow = None
        self.setup_ui()
        self.setup_signals()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.group = QGroupBox("Execution Controls")
        group_layout = QVBoxLayout(self.group)

        # Status Label
        self.status_label = QLabel("Status: IDLE")
        self.status_label.setStyleSheet("font-weight: bold; color: blue;")
        group_layout.addWidget(self.status_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        group_layout.addWidget(self.progress_bar)

        # Repeat Count
        repeat_layout = QHBoxLayout()
        repeat_layout.addWidget(QLabel("Repeat Count (0=Inf):"))
        self.repeat_spin = QSpinBox()
        self.repeat_spin.setRange(0, 9999)
        self.repeat_spin.setValue(1)
        repeat_layout.addWidget(self.repeat_spin)
        group_layout.addLayout(repeat_layout)

        # Control Buttons
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ Start (F5)")
        self.btn_pause = QPushButton("⏸ Pause (F6)")
        self.btn_stop = QPushButton("⏹ Stop (Esc)")
        
        self.btn_start.clicked.connect(self._on_start_clicked)
        self.btn_pause.clicked.connect(self._on_pause_clicked)
        self.btn_stop.clicked.connect(self._on_stop_clicked)
        
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_pause)
        btn_layout.addWidget(self.btn_stop)
        group_layout.addLayout(btn_layout)

        layout.addWidget(self.group)

    def setup_signals(self):
        # Connect to Coordinator (Engine) signals
        self.coordinator.state_changed.connect(self._on_state_changed)
        self.coordinator.progress_updated.connect(self._on_progress_updated)
        self.coordinator.flow_error.connect(self._on_flow_error)

    def set_flow(self, flow):
        self.current_flow = flow
        # Only enable start if not already running
        state = self.coordinator.get_engine_state()
        if state in [EngineState.IDLE, EngineState.COMPLETED, EngineState.STOPPED, EngineState.ERROR]:
            self.btn_start.setEnabled(flow is not None)

    def _on_start_clicked(self):
        if self.current_flow:
            self.current_flow.repeat_count = self.repeat_spin.value()
            self.coordinator.start_flow(self.current_flow)

    def _on_pause_clicked(self):
        state = self.coordinator.get_engine_state()
        if state == EngineState.RUNNING:
            self.coordinator.pause_flow()
        elif state == EngineState.PAUSED:
            self.coordinator.resume_flow()

    def _on_stop_clicked(self):
        self.coordinator.stop_flow()

    @pyqtSlot(EngineState)
    def _on_state_changed(self, state):
        self.status_label.setText(f"Status: {state.name}")
        self.status_label.setStyleSheet("font-weight: bold; color: blue;")
        
        is_running = state == EngineState.RUNNING
        is_paused = state == EngineState.PAUSED
        
        self.btn_start.setEnabled(state in [EngineState.IDLE, EngineState.COMPLETED, EngineState.STOPPED, EngineState.ERROR] and self.current_flow is not None)
        self.btn_pause.setEnabled(is_running or is_paused)
        self.btn_stop.setEnabled(is_running or is_paused)
        
        if is_paused:
            self.btn_pause.setText("▶ Resume")
        else:
            self.btn_pause.setText("⏸ Pause")

        if state == EngineState.COMPLETED:
            self.progress_bar.setValue(100)
        elif state == EngineState.IDLE:
            self.progress_bar.setValue(0)

    @pyqtSlot(int, int)
    def _on_progress_updated(self, current, total):
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.status_label.setText(f"Status: RUNNING ({current}/{total})")

    @pyqtSlot(str)
    def _on_flow_error(self, error_msg):
        self.status_label.setText(f"멈춤: {error_msg}")
        self.status_label.setStyleSheet("font-weight: bold; color: #D32F2F; border: 1px solid red; padding: 2px;")
        # Also update the progress bar to show failure
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #FFCDD2; }")
