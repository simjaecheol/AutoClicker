from pynput.keyboard import Key, KeyCode, Controller
import time
from typing import Union, List

class VirtualKeyboard:
    def __init__(self):
        self.keyboard = Controller()

    def _get_key(self, key_str: str) -> Union[Key, str]:
        """Converts string key representation to pynput Key or char."""
        # Handle special numeric strings like "<21>" (pynput's internal representation for some keys)
        if key_str.startswith("<") and key_str.endswith(">"):
            try:
                vk_code = int(key_str[1:-1])
                # Safely try to create a KeyCode, fallback to string if it fails
                try:
                    return KeyCode.from_vk(vk_code)
                except Exception:
                    return key_str 
            except ValueError:
                pass

        if hasattr(Key, key_str):
            return getattr(Key, key_str)
        return key_str

    def press(self, key: str):
        k = self._get_key(key)
        self.keyboard.press(k)

    def release(self, key: str):
        k = self._get_key(key)
        self.keyboard.release(k)

    def type_text(self, text: str, interval: float = 0.05):
        for char in text:
            self.keyboard.type(char)
            if interval > 0:
                time.sleep(interval)

    def hotkey(self, *keys: str):
        """Executes a combination of keys, e.g., hotkey('ctrl', 'c')"""
        k_objs = [self._get_key(k) for k in keys]
        
        # Press all keys
        for k in k_objs:
            self.keyboard.press(k)
        
        # Release all keys in reverse order
        for k in reversed(k_objs):
            self.keyboard.release(k)

    def release_all(self):
        """Emergency release of modifier keys if needed."""
        modifiers = [Key.ctrl, Key.shift, Key.alt, Key.cmd]
        for m in modifiers:
            self.keyboard.release(m)
