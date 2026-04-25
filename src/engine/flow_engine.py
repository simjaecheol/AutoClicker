import time
import threading
from enum import Enum, auto
from PyQt5.QtCore import QObject, pyqtSignal
from models.flow import Flow
from models.action import Action
from engine.action_registry import ActionRegistry

class EngineState(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()
    COMPLETED = auto()
    ERROR = auto()

class FlowEngine(QObject):
    # Signals
    state_changed = pyqtSignal(EngineState)
    step_started = pyqtSignal(int, Action)    # (index, action)
    step_completed = pyqtSignal(int, Action)
    flow_completed = pyqtSignal()
    flow_error = pyqtSignal(str)
    progress_updated = pyqtSignal(int, int)   # (current, total)

    def __init__(self, registry: ActionRegistry):
        super().__init__()
        self.registry = registry
        self.state = EngineState.IDLE
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set() # Initially not paused
        self._thread: threading.Thread = None

    def start(self, flow: Flow):
        if self.state == EngineState.RUNNING:
            return

        self._stop_event.clear()
        self._pause_event.set()
        self.state = EngineState.RUNNING
        self.state_changed.emit(self.state)
        
        self._thread = threading.Thread(target=self._run_flow, args=(flow,), daemon=True)
        self._thread.start()

    def pause(self):
        if self.state == EngineState.RUNNING:
            self._pause_event.clear()
            self.state = EngineState.PAUSED
            self.state_changed.emit(self.state)

    def resume(self):
        if self.state == EngineState.PAUSED:
            self._pause_event.set()
            self.state = EngineState.RUNNING
            self.state_changed.emit(self.state)

    def stop(self):
        self._stop_event.set()
        self._pause_event.set() # Resume if paused to allow stop
        self.state = EngineState.STOPPED
        self.state_changed.emit(self.state)

    def _get_user_friendly_error(self, error: Exception) -> str:
        """Translates technical errors into abstract, non-technical messages for users."""
        error_str = str(error).lower()
        
        if "permission" in error_str or "access denied" in error_str:
            return "시스템 보안 설정이 자동 제어를 차단했습니다. '관리자 권한'으로 프로그램을 다시 실행해 보세요."
        
        if "invalid" in error_str or "coordinate" in error_str:
            return "클릭하려는 위치가 화면 밖이거나 잘못되었습니다. 좌표 설정을 다시 확인해 주세요."
            
        if "key" in error_str:
            return "사용할 수 없는 키가 입력되었거나 키보드 연결에 문제가 있습니다."
            
        if "device" in error_str or "not found" in error_str:
            return "마우스나 키보드 장치를 찾을 수 없거나 다른 프로그램이 사용 중입니다."

        if "21" in error_str:
            return "시스템과 장치 간의 통신에 일시적인 문제가 발생했습니다. (장치 응답 지연)"
            
        # Default fallback for unknown errors
        return f"작업을 수행하는 중에 예기치 않은 방해를 받았습니다. ({str(error)})"

    def _run_flow(self, flow: Flow):
        try:
            total_steps = len(flow.steps)
            current_repeat = 0
            
            while not self._stop_event.is_set():
                for i, action in enumerate(flow.steps):
                    # Check for pause
                    self._pause_event.wait()
                    if self._stop_event.is_set():
                        break

                    self.step_started.emit(i, action)
                    self.progress_updated.emit(i + 1, total_steps)
                    
                    try:
                        self.registry.execute(action)
                    except Exception as e:
                        user_error = self._get_user_friendly_error(e)
                        self.state = EngineState.ERROR
                        self.state_changed.emit(self.state)
                        self.flow_error.emit(user_error)
                        return

                    self.step_completed.emit(i, action)

                current_repeat += 1
                if flow.repeat_count != 0 and current_repeat >= flow.repeat_count:
                    break
                
                if flow.repeat_interval > 0 and not self._stop_event.is_set():
                    time.sleep(flow.repeat_interval)

            if not self._stop_event.is_set():
                self.state = EngineState.COMPLETED
                self.state_changed.emit(self.state)
                self.flow_completed.emit()
            else:
                self.state = EngineState.IDLE
                self.state_changed.emit(self.state)

        except Exception as e:
            self.state = EngineState.ERROR
            self.state_changed.emit(self.state)
            self.flow_error.emit(str(e))
