from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict

class EventType(Enum):
    MOUSE_CLICK = "mouse_click"
    MOUSE_RELEASE = "mouse_release"
    MOUSE_MOVE = "mouse_move"
    MOUSE_SCROLL = "mouse_scroll"
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"

@dataclass
class RawEvent:
    type: EventType
    timestamp: float
    data: Dict[str, Any]
