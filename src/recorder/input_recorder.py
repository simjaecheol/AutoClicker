from PyQt5.QtCore import QObject, pyqtSignal
from typing import List, Callable, Optional
from models.raw_event import RawEvent
from recorder.mouse_listener import MouseListener
from recorder.keyboard_listener import KeyboardListener

class RecorderState:
    IDLE = "IDLE"
    RECORDING = "RECORDING"
    PAUSED = "PAUSED"

class InputRecorder(QObject):
    # Signals for UI updates
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    recording_paused = pyqtSignal(bool) # True if paused, False if resumed
    event_captured = pyqtSignal(RawEvent)
    
    def __init__(self):
        super().__init__()
        self.state = RecorderState.IDLE
        self._events: List[RawEvent] = []
        
        # Initialize listeners with our callback
        self.mouse_listener = MouseListener(self._on_event)
        self.keyboard_listener = KeyboardListener(self._on_event)
        
        self.record_mouse_move = False # Default to False to reduce noise

    def start_recording(self):
        if self.state == RecorderState.RECORDING:
            return
            
        self._events.clear()
        self.state = RecorderState.RECORDING
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        self.recording_started.emit()

    def stop_recording(self) -> List[RawEvent]:
        if self.state == RecorderState.IDLE:
            return []
            
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
        self.state = RecorderState.IDLE
        
        self.recording_stopped.emit()
        return self._events.copy()

    def pause_recording(self):
        if self.state == RecorderState.RECORDING:
            self.mouse_listener.pause()
            self.keyboard_listener.pause()
            self.state = RecorderState.PAUSED
            self.recording_paused.emit(True)

    def resume_recording(self):
        if self.state == RecorderState.PAUSED:
            self.mouse_listener.resume()
            self.keyboard_listener.resume()
            self.state = RecorderState.RECORDING
            self.recording_paused.emit(False)

    def is_recording(self) -> bool:
        return self.state == RecorderState.RECORDING

    def is_active(self) -> bool:
        """Returns True if in any recording session (RECORDING or PAUSED)."""
        return self.state in (RecorderState.RECORDING, RecorderState.PAUSED)

    def get_captured_events(self) -> List[RawEvent]:
        return self._events.copy()

    def _on_event(self, event: RawEvent):
        """Callback for listeners. Filters and stores events, then emits signal."""
        if not self.record_mouse_move and event.type == event.type.MOUSE_MOVE:
            return
            
        self._events.append(event)
        # Emit signal for real-time UI updates (e.g., event counter)
        # Note: This is called from a background thread (pynput listener thread)
        # PyQt signals are thread-safe and will be queued to the main thread
        self.event_captured.emit(event)
