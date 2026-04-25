import os
from PyQt5.QtCore import QObject, pyqtSignal
from models.flow import Flow
from models.action import Action
from drivers.virtual_mouse import VirtualMouse
from drivers.virtual_keyboard import VirtualKeyboard
from engine.action_registry import ActionRegistry
from engine.flow_engine import FlowEngine, EngineState
from storage.flow_repository import FlowRepository

# Recording imports
from recorder.input_recorder import InputRecorder
from recorder.action_converter import ActionConverter
from recorder.post_processor import RecordingPostProcessor
from recorder.event_aggregator import AggregatorConfig

class Coordinator(QObject):
    # Proxy signals from engine
    state_changed = pyqtSignal(EngineState)
    step_started = pyqtSignal(int, Action)
    step_completed = pyqtSignal(int, Action)
    flow_completed = pyqtSignal()
    flow_error = pyqtSignal(str)
    progress_updated = pyqtSignal(int, int)

    # Recording signals
    recording_event_captured = pyqtSignal(object) # RawEvent
    recording_completed = pyqtSignal(Flow)

    def __init__(self):
        super().__init__()
        # Drivers
        self.mouse = VirtualMouse()
        self.keyboard = VirtualKeyboard()
        
        # Engine
        self.registry = ActionRegistry(self.mouse, self.keyboard)
        self.engine = FlowEngine(self.registry)
        
        # Storage
        base_dir = os.path.join(os.path.expanduser("~"), ".autoclicker", "flows")
        self.repository = FlowRepository(base_dir)
        
        # Recording Modules
        self.recorder = InputRecorder()
        self.action_converter = ActionConverter()
        self.post_processor = RecordingPostProcessor()
        self.aggregator_config = AggregatorConfig()
        
        # Connect engine signals
        self.engine.state_changed.connect(self.state_changed.emit)
        self.engine.step_started.connect(self.step_started.emit)
        self.engine.step_completed.connect(self.step_completed.emit)
        self.engine.flow_completed.connect(self.flow_completed.emit)
        self.engine.flow_error.connect(self.flow_error.emit)
        self.engine.progress_updated.connect(self.progress_updated.emit)
        
        # Connect recording signals
        self.recorder.event_captured.connect(self.recording_event_captured.emit)

    # Flow Management
    def get_all_flows(self):
        return self.repository.load_all()

    def save_flow(self, flow: Flow):
        self.repository.save(flow)

    def delete_flow(self, flow_id: str):
        self.repository.delete(flow_id)

    # Execution Control
    def start_flow(self, flow: Flow):
        self.engine.start(flow)

    def pause_flow(self):
        self.engine.pause()

    def resume_flow(self):
        self.engine.resume()

    def stop_flow(self):
        self.engine.stop()

    def get_engine_state(self) -> EngineState:
        return self.engine.state

    # Recording Control
    def start_recording(self):
        self.recorder.start_recording()
        
    def stop_recording(self) -> Flow:
        raw_events = self.recorder.stop_recording()
        
        # 1. Convert raw events to actions
        actions = self.action_converter.convert(raw_events, self.aggregator_config)
        
        # 2. Post-process to merge/refine actions
        refined_actions = self.post_processor.process(actions)
        
        # 3. Create a new flow from these actions
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_flow = Flow(name=f"Recorded Flow {timestamp}", steps=refined_actions)
        
        self.save_flow(new_flow)
        self.recording_completed.emit(new_flow)
        return new_flow

    def pause_recording(self):
        self.recorder.pause_recording()

    def resume_recording(self):
        self.recorder.resume_recording()

    def is_recording(self) -> bool:
        return self.recorder.is_recording()

    def is_active(self) -> bool:
        """Returns True if in any recording session (RECORDING or PAUSED)."""
        return self.recorder.is_active()
