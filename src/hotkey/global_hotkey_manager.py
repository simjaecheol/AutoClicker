from pynput import keyboard
from typing import Callable, Dict

class GlobalHotkeyManager:
    def __init__(self):
        self._hotkeys: Dict[str, Callable] = {}
        self._listener = None

    def register(self, hotkeys_dict: Dict[str, Callable]):
        """
        Register a dictionary of hotkeys and their callbacks.
        Example: {'<ctrl>+<shift>+r': on_record_toggle}
        """
        self._hotkeys.update(hotkeys_dict)
        self._restart_listener()

    def unregister_all(self):
        self._hotkeys.clear()
        if self._listener:
            self._listener.stop()
            self._listener = None

    def pause(self):
        """Temporarily stop the hotkey listener to avoid conflicts with KeyboardListener."""
        if self._listener:
            self._listener.stop()
            self._listener = None

    def resume(self):
        """Re-start the hotkey listener after recording is done."""
        if self._hotkeys and self._listener is None:
            self._restart_listener()

    def _restart_listener(self):
        if self._listener:
            self._listener.stop()
            
        if self._hotkeys:
            self._listener = keyboard.GlobalHotKeys(self._hotkeys)
            self._listener.start()

