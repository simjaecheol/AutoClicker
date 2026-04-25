from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QStatusBar, QMenuBar, QMenu, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os
from ui.flow_list_widget import FlowListWidget
from ui.step_editor_widget import StepEditorWidget
from ui.action_palette_widget import ActionPaletteWidget
from ui.execution_controls_widget import ExecutionControlsWidget
from ui.recording_toolbar import RecordingToolbar
from ui.recording_overlay import RecordingOverlay
from hotkey.global_hotkey_manager import GlobalHotkeyManager
from utils.path_helper import get_resource_path

class MainWindow(QMainWindow):
    def __init__(self, coordinator):
        super().__init__()
        self.coordinator = coordinator
        
        self.hotkey_manager = GlobalHotkeyManager()
        self.overlay = RecordingOverlay()
        
        self.setWindowTitle("AutoClicker — Flow-Based Automation")
        self.resize(1000, 700)
        
        # Set Window Icon
        icon_path = get_resource_path(os.path.join("resources", "icons", "logo.png"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()

    def setup_ui(self):
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create all widgets first
        self.recording_toolbar = RecordingToolbar(self.coordinator, self.hotkey_manager, self.overlay)
        self.flow_list = FlowListWidget(self.coordinator)
        self.step_editor = StepEditorWidget(self.coordinator)
        self.action_palette = ActionPaletteWidget(self.coordinator)
        self.execution_controls = ExecutionControlsWidget(self.coordinator)

        # Connect signals
        self.flow_list.flow_selected.connect(self.step_editor.set_flow)
        self.flow_list.flow_selected.connect(self.action_palette.set_flow)
        self.flow_list.flow_selected.connect(self.execution_controls.set_flow)
        self.action_palette.action_added.connect(self.step_editor.refresh_steps)
        
        # Recording signals
        self.recording_toolbar.request_minimize.connect(self.showMinimized)
        self.recording_toolbar.request_restore.connect(self.showNormal)
        self.coordinator.recording_completed.connect(self._on_recording_completed)
        
        # Toolbar Section
        main_layout.addWidget(self.recording_toolbar)
        
        # Top Section (Splitter for Flow List and Step Editor)
        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.addWidget(self.flow_list)
        top_splitter.addWidget(self.step_editor)
        top_splitter.setStretchFactor(1, 2)

        # Bottom Section
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.action_palette, 1)
        bottom_layout.addWidget(self.execution_controls, 2)

        # Add to main layout
        main_layout.addWidget(top_splitter, 3)
        main_layout.addLayout(bottom_layout, 1)

    def setup_menu(self):
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Flow", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        save_action = QAction("&Save Flow", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About", self)
        help_menu.addAction(about_action)

    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _on_recording_completed(self, new_flow):
        self.flow_list.refresh_list()
        
        # Find and select the newly created flow
        for i in range(self.flow_list.list_widget.count()):
            item = self.flow_list.list_widget.item(i)
            if item.data(100).id == new_flow.id:
                self.flow_list.list_widget.setCurrentRow(i)
                break
        
        self.status_bar.showMessage(f"Recording saved as '{new_flow.name}' with {len(new_flow.steps)} steps.", 5000)
