import time
from pynput import keyboard
from typing import Callable, Optional
from models.raw_event import RawEvent, EventType

class KeyboardListener:
    def __init__(self, callback: Callable[[RawEvent], None]):
        self.callback = callback
        self._listener: Optional[keyboard.Listener] = None
        self._is_recording = False

    def start(self):
        if self._listener is not None:
            self.stop()
            
        self._is_recording = True
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.start()

    def stop(self):
        self._is_recording = False
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def pause(self):
        self._is_recording = False

    def resume(self):
        self._is_recording = True

    def _get_key_name(self, key) -> str:
        """Convert pynput key object to a string representation.
        
        Priority order:
        1. char attribute (normal characters like 'a', '1', '!')
        2. name attribute (special keys like 'enter', 'shift', 'ctrl_l')
        3. vk code fallback (IME input, Han/Eng toggle, etc.)
        """
        # 1) Normal character keys — always check char first
        if hasattr(key, 'char') and key.char is not None:
            return key.char
        
        # 2) Named special keys (enter, shift, ctrl, etc.)
        if hasattr(key, 'name') and key.name is not None:
            return key.name
        
        # 3) VK code fallback (IME/한글 input where char is None)
        if hasattr(key, 'vk') and key.vk is not None:
            return f"<{key.vk}>"
        
        return str(key)

    def _on_press(self, key):
        if not self._is_recording:
            return
            
        event = RawEvent(
            type=EventType.KEY_PRESS,
            timestamp=time.time(),
            data={"key": self._get_key_name(key)}
        )
        self.callback(event)

    def _on_release(self, key):
        if not self._is_recording:
            return
            
        event = RawEvent(
            type=EventType.KEY_RELEASE,
            timestamp=time.time(),
            data={"key": self._get_key_name(key)}
        )
        self.callback(event)
