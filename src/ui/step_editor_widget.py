from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHeaderView, QLabel)
from PyQt5.QtCore import Qt
from models.flow import Flow
from models.action import Action

class StepEditorWidget(QWidget):
    def __init__(self, coordinator, parent=None):
        super().__init__(parent)
        self.coordinator = coordinator
        self.current_flow = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel("Steps: No Flow Selected")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        layout.addWidget(self.title_label)

        # Step Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Type", "Parameters", "Delay", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) # Params gets most space
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.table)

        # Control Buttons
        btn_layout = QHBoxLayout()
        self.btn_up = QPushButton("▲ Move Up")
        self.btn_down = QPushButton("▼ Move Down")
        self.btn_remove = QPushButton("✕ Remove")
        
        self.btn_up.clicked.connect(self._move_step_up)
        self.btn_down.clicked.connect(self._move_step_down)
        self.btn_remove.clicked.connect(self._remove_step)
        
        btn_layout.addWidget(self.btn_up)
        btn_layout.addWidget(self.btn_down)
        btn_layout.addWidget(self.btn_remove)
        layout.addLayout(btn_layout)

    def set_flow(self, flow: Flow):
        self.current_flow = flow
        if flow:
            self.title_label.setText(f"Steps: {flow.name}")
            self.refresh_steps()
        else:
            self.title_label.setText("Steps: No Flow Selected")
            self.table.setRowCount(0)

    def refresh_steps(self):
        if not self.current_flow:
            return
            
        self.table.setRowCount(0)
        for i, step in enumerate(self.current_flow.steps):
            self.table.insertRow(i)
            
            # Action Type
            type_item = QTableWidgetItem(step.type.value)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable) # Read-only
            self.table.setItem(i, 0, type_item)
            
            # Parameters (Simplified string representation)
            params_str = ", ".join([f"{k}: {v}" for k, v in step.params.items()])
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 1, params_item)
            
            # Delay
            delay_item = QTableWidgetItem(f"{step.delay_after}s")
            self.table.setItem(i, 2, delay_item)
            
            # Description
            desc_item = QTableWidgetItem(step.description)
            self.table.setItem(i, 3, desc_item)

    def _move_step_up(self):
        row = self.table.currentRow()
        if row > 0 and self.current_flow:
            steps = self.current_flow.steps
            steps[row], steps[row-1] = steps[row-1], steps[row]
            self.coordinator.save_flow(self.current_flow)
            self.refresh_steps()
            self.table.setCurrentCell(row-1, 0)

    def _move_step_down(self):
        row = self.table.currentRow()
        if self.current_flow and 0 <= row < len(self.current_flow.steps) - 1:
            steps = self.current_flow.steps
            steps[row], steps[row+1] = steps[row+1], steps[row]
            self.coordinator.save_flow(self.current_flow)
            self.refresh_steps()
            self.table.setCurrentCell(row+1, 0)

    def _remove_step(self):
        row = self.table.currentRow()
        if row >= 0 and self.current_flow:
            self.current_flow.steps.pop(row)
            self.coordinator.save_flow(self.current_flow)
            self.refresh_steps()
