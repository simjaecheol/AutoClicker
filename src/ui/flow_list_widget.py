from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QListWidgetItem, QInputDialog, QMessageBox)
from PyQt5.QtCore import pyqtSignal
from models.flow import Flow

class FlowListWidget(QWidget):
    # Signal emitted when a flow is selected (object to allow None)
    flow_selected = pyqtSignal(object)

    def __init__(self, coordinator, parent=None):
        super().__init__(parent)
        self.coordinator = coordinator
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title/Label could be added here
        self.list_widget = QListWidget()
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.list_widget)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("+ New")
        self.btn_delete = QPushButton("Delete")
        
        self.btn_new.clicked.connect(self._create_new_flow)
        self.btn_delete.clicked.connect(self._delete_selected_flow)
        
        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)

    def refresh_list(self):
        """Reloads flow list from the repository."""
        self.list_widget.clear()
        flows = self.coordinator.get_all_flows()
        for flow in flows:
            item = QListWidgetItem(flow.name)
            item.setData(100, flow) # Store the Flow object in the item
            self.list_widget.addItem(item)

    def _on_selection_changed(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            flow = selected_items[0].data(100)
            self.flow_selected.emit(flow)

    def _create_new_flow(self):
        name, ok = QInputDialog.getText(self, "New Flow", "Enter flow name:")
        if ok and name:
            new_flow = Flow(name=name)
            self.coordinator.save_flow(new_flow)
            self.refresh_list()
            # Select the newly created item
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if item.data(100).id == new_flow.id:
                    self.list_widget.setCurrentRow(i)
                    break

    def _delete_selected_flow(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
            
        flow = selected_items[0].data(100)
        reply = QMessageBox.question(self, "Delete Flow", 
                                   f"Are you sure you want to delete '{flow.name}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.coordinator.delete_flow(flow.id)
            self.refresh_list()
            self.flow_selected.emit(None) # Notify that no flow is selected
