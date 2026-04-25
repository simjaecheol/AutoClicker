import time
from typing import Dict, Callable, Any
from models.action import Action, ActionType
from drivers.virtual_mouse import VirtualMouse
from drivers.virtual_keyboard import VirtualKeyboard

class ActionRegistry:
    def __init__(self, mouse: VirtualMouse, keyboard: VirtualKeyboard):
        self.mouse = mouse
        self.keyboard = keyboard
        self._handlers: Dict[ActionType, Callable[[Action], None]] = {}
        self._setup_default_handlers()

    def register(self, action_type: ActionType, handler: Callable[[Action], None]):
        self._handlers[action_type] = handler

    def execute(self, action: Action):
        handler = self._handlers.get(action.type)
        if handler:
            handler(action)
            if action.delay_after > 0:
                time.sleep(action.delay_after)
        else:
            raise ValueError(f"No handler registered for action type: {action.type}")

    def _setup_default_handlers(self):
        # Mouse Handlers
        self.register(ActionType.LEFT_CLICK, self._handle_left_click)
        self.register(ActionType.RIGHT_CLICK, self._handle_right_click)
        self.register(ActionType.DOUBLE_CLICK, self._handle_double_click)
        self.register(ActionType.DRAG, self._handle_drag)
        self.register(ActionType.SCROLL_UP, self._handle_scroll_up)
        self.register(ActionType.SCROLL_DOWN, self._handle_scroll_down)
        
        # Keyboard Handlers
        self.register(ActionType.KEY_PRESS, self._handle_key_press)
        self.register(ActionType.KEY_RELEASE, self._handle_key_release)
        self.register(ActionType.KEY_COMBO, self._handle_key_combo)
        self.register(ActionType.TEXT_INPUT, self._handle_text_input)
        
        # Other Handlers
        self.register(ActionType.DELAY, self._handle_delay)

    def _handle_left_click(self, action: Action):
        x, y = action.params.get("x"), action.params.get("y")
        if x is not None and y is not None:
            self.mouse.click_at(x, y)
        else:
            self.mouse.click()

    def _handle_right_click(self, action: Action):
        x, y = action.params.get("x"), action.params.get("y")
        if x is not None and y is not None:
            self.mouse.right_click_at(x, y)
        else:
            self.mouse.right_click()

    def _handle_double_click(self, action: Action):
        x, y = action.params.get("x"), action.params.get("y")
        if x is not None and y is not None:
            self.mouse.double_click_at(x, y)
        else:
            self.mouse.double_click()

    def _handle_drag(self, action: Action):
        params = action.params
        self.mouse.drag(params["from_x"], params["from_y"], params["to_x"], params["to_y"])

    def _handle_scroll_up(self, action: Action):
        amount = action.params.get("amount", 1)
        self.mouse.scroll(0, amount)

    def _handle_scroll_down(self, action: Action):
        amount = action.params.get("amount", 1)
        self.mouse.scroll(0, -amount)

    def _handle_key_press(self, action: Action):
        # Tap (press + release) since KEY_RELEASE is no longer a separate action
        self.keyboard.press(action.params["key"])
        self.keyboard.release(action.params["key"])

    def _handle_key_release(self, action: Action):
        self.keyboard.release(action.params["key"])

    def _handle_key_combo(self, action: Action):
        self.keyboard.hotkey(*action.params["keys"])

    def _handle_text_input(self, action: Action):
        self.keyboard.type_text(action.params["text"], action.params.get("interval", 0.05))

    def _handle_delay(self, action: Action):
        time.sleep(action.params.get("seconds", 0.0))
