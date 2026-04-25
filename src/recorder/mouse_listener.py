import time
from pynput import mouse
from typing import Callable, Optional
from models.raw_event import RawEvent, EventType

class MouseListener:
    def __init__(self, callback: Callable[[RawEvent], None]):
        self.callback = callback
        self._listener: Optional[mouse.Listener] = None
        self._is_recording = False

    def start(self):
        if self._listener is not None:
            self.stop()
            
        self._is_recording = True
        self._listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll
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

    def _on_move(self, x, y):
        if not self._is_recording:
            return
        event = RawEvent(
            type=EventType.MOUSE_MOVE,
            timestamp=time.time(),
            data={"x": int(x), "y": int(y)}
        )
        self.callback(event)

    def _on_click(self, x, y, button, pressed):
        if not self._is_recording:
            return
            
        event_type = EventType.MOUSE_CLICK if pressed else EventType.MOUSE_RELEASE
        # Convert button to a simpler string representation
        btn_name = "left" if button == mouse.Button.left else ("right" if button == mouse.Button.right else "middle")
        
        event = RawEvent(
            type=event_type,
            timestamp=time.time(),
            data={"x": int(x), "y": int(y), "button": btn_name}
        )
        self.callback(event)

    def _on_scroll(self, x, y, dx, dy):
        if not self._is_recording:
            return
        event = RawEvent(
            type=EventType.MOUSE_SCROLL,
            timestamp=time.time(),
            data={"x": int(x), "y": int(y), "dx": int(dx), "dy": int(dy)}
        )
        self.callback(event)
