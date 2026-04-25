from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

class ActionType(Enum):
    LEFT_CLICK = "left_click"
    RIGHT_CLICK = "right_click"
    DOUBLE_CLICK = "double_click"
    DRAG = "drag"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    KEY_COMBO = "key_combo"        # e.g., Ctrl+C
    TEXT_INPUT = "text_input"
    DELAY = "delay"

@dataclass
class Action:
    type: ActionType
    params: Dict[str, Any] = field(default_factory=dict) # Parameters (coordinates, keys, text, etc.)
    delay_after: float = 0.0                             # Wait time after execution (seconds)
    description: str = ""                                # User note

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "params": self.params,
            "delay_after": self.delay_after,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        return cls(
            type=ActionType(data["type"]),
            params=data.get("params", {}),
            delay_after=data.get("delay_after", 0.0),
            description=data.get("description", "")
        )
