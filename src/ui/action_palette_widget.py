from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                             QLabel, QLineEdit, QDoubleSpinBox, QPushButton, 
                             QGroupBox, QFormLayout, QStackedWidget)
from PyQt5.QtCore import pyqtSignal
from models.action import Action, ActionType
from ui.coordinate_picker import CoordinatePicker

class ActionPaletteWidget(QWidget):
    # Signal emitted when a new action is added to the flow
    action_added = pyqtSignal()

    def __init__(self, coordinator, parent=None):
        super().__init__(parent)
        self.coordinator = coordinator
        self.current_flow = None
        self.picker = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.group = QGroupBox("Add Action")
        group_layout = QVBoxLayout(self.group)
        
        # Action Type Selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        for action_type in ActionType:
            self.type_combo.addItem(action_type.value, action_type)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.type_combo)
        group_layout.addLayout(type_layout)

        # Dynamic Parameter Inputs (Stacked Widget)
        self.param_stack = QStackedWidget()
        self._setup_param_inputs()
        group_layout.addWidget(self.param_stack)

        # Common Fields (Delay After, Description)
        common_layout = QFormLayout()
        self.delay_input = QDoubleSpinBox()
        self.delay_input.setSuffix(" s")
        self.delay_input.setSingleStep(0.1)
        self.delay_input.setValue(0.5)
        common_layout.addRow("Delay After:", self.delay_input)
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description (optional)")
        common_layout.addRow("Description:", self.desc_input)
        group_layout.addLayout(common_layout)

        # Add Button
        self.btn_add = QPushButton("Add Step")
        self.btn_add.clicked.connect(self._add_action)
        self.btn_add.setEnabled(False)
        group_layout.addWidget(self.btn_add)

        layout.addWidget(self.group)

    def _setup_param_inputs(self):
        # 1. Click Parameters (X, Y)
        self.click_form = QWidget()
        l1 = QFormLayout(self.click_form)
        
        coord_layout = QHBoxLayout()
        self.input_x = QLineEdit("0")
        self.input_y = QLineEdit("0")
        self.btn_pick = QPushButton("Pick")
        self.btn_pick.clicked.connect(self._start_picking)
        
        coord_layout.addWidget(QLabel("X:"))
        coord_layout.addWidget(self.input_x)
        coord_layout.addWidget(QLabel("Y:"))
        coord_layout.addWidget(self.input_y)
        coord_layout.addWidget(self.btn_pick)
        
        l1.addRow("Coordinates:", coord_layout)
        self.param_stack.addWidget(self.click_form)
        
        # 2. Text Input Parameters
        self.text_form = QWidget()
        l2 = QFormLayout(self.text_form)
        self.input_text = QLineEdit()
        l2.addRow("Text to Type:", self.input_text)
        self.param_stack.addWidget(self.text_form)
        
        # 3. Key/Hotkey Parameters
        self.key_form = QWidget()
        l3 = QFormLayout(self.key_form)
        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText("e.g., ctrl+c or a")
        l3.addRow("Key(s):", self.input_key)
        self.param_stack.addWidget(self.key_form)

        # Mapping Type to Stack Index
        self.type_map = {
            ActionType.LEFT_CLICK: 0,
            ActionType.RIGHT_CLICK: 0,
            ActionType.DOUBLE_CLICK: 0,
            ActionType.TEXT_INPUT: 1,
            ActionType.KEY_PRESS: 2,
            ActionType.KEY_RELEASE: 2,
            ActionType.KEY_COMBO: 2,
        }

    def _on_type_changed(self):
        action_type = self.type_combo.currentData()
        idx = self.type_map.get(action_type, 0)
        self.param_stack.setCurrentIndex(idx)

    def set_flow(self, flow):
        self.current_flow = flow
        self.btn_add.setEnabled(flow is not None)

    def _add_action(self):
        if not self.current_flow:
            return
            
        action_type = self.type_combo.currentData()
        params = {}
        
        idx = self.param_stack.currentIndex()
        if idx == 0: # Click
            try:
                params = {"x": int(self.input_x.text()), "y": int(self.input_y.text())}
            except ValueError:
                params = {"x": 0, "y": 0}
        elif idx == 1: # Text
            params = {"text": self.input_text.text()}
        elif idx == 2: # Keys
            key_val = self.input_key.text()
            if action_type == ActionType.KEY_COMBO:
                params = {"keys": [k.strip() for k in key_val.split('+')]}
            else:
                params = {"key": key_val}
            
        action = Action(
            type=action_type,
            params=params,
            delay_after=self.delay_input.value(),
            description=self.desc_input.text()
        )
        
        self.current_flow.steps.append(action)
        self.coordinator.save_flow(self.current_flow)
        self.action_added.emit()

    def _start_picking(self):
        self.picker = CoordinatePicker()
        self.picker.coordinate_picked.connect(self._on_coordinate_picked)
        self.picker.show()

    def _on_coordinate_picked(self, x, y):
        self.input_x.setText(str(x))
        self.input_y.setText(str(y))
